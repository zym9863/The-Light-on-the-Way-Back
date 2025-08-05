"""
假象回廊服务模块
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from ..models import FacadeIdentity, FacadeContent, FacadeApplause
from ..encryption import generate_identity_token, hash_ip
from ..config import FACADE_LIFETIME_HOURS, MAX_FACADE_CONTENT_LENGTH, MAX_APPLAUSE_PER_CONTENT

class FacadeGalleryService:
    """假象回廊服务类"""
    
    async def create_identity(
        self,
        db: AsyncSession,
        creator_ip: Optional[str] = None
    ) -> FacadeIdentity:
        """
        创建假象身份
        
        Args:
            db: 数据库会话
            creator_ip: 创建者IP
            
        Returns:
            创建的假象身份
        """
        # 生成唯一的身份令牌
        identity_token = generate_identity_token()
        
        # 确保令牌唯一性
        while True:
            result = await db.execute(
                select(FacadeIdentity).where(
                    FacadeIdentity.identity_token == identity_token
                )
            )
            if not result.scalar_one_or_none():
                break
            identity_token = generate_identity_token()
        
        # 创建假象身份
        identity = FacadeIdentity(
            identity_token=identity_token,
            expires_at=datetime.utcnow() + timedelta(hours=FACADE_LIFETIME_HOURS),
            creator_ip_hash=hash_ip(creator_ip) if creator_ip else None
        )
        
        db.add(identity)
        await db.commit()
        await db.refresh(identity)
        
        return identity
    
    async def get_identity(
        self,
        db: AsyncSession,
        identity_token: str
    ) -> Optional[FacadeIdentity]:
        """
        获取假象身份
        
        Args:
            db: 数据库会话
            identity_token: 身份令牌
            
        Returns:
            假象身份对象或None
        """
        result = await db.execute(
            select(FacadeIdentity).where(
                and_(
                    FacadeIdentity.identity_token == identity_token,
                    FacadeIdentity.is_expired == False,
                    FacadeIdentity.expires_at > datetime.utcnow()
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def create_content(
        self,
        db: AsyncSession,
        identity_token: str,
        content_text: Optional[str] = None,
        image_path: Optional[str] = None
    ) -> FacadeContent:
        """
        创建假象回廊内容
        
        Args:
            db: 数据库会话
            identity_token: 身份令牌
            content_text: 文本内容
            image_path: 图片路径
            
        Returns:
            创建的内容对象
            
        Raises:
            ValueError: 如果参数无效或身份无效
        """
        # 验证身份
        identity = await self.get_identity(db, identity_token)
        if not identity:
            raise ValueError("身份无效或已过期")
        
        # 验证内容
        if not content_text and not image_path:
            raise ValueError("必须提供文本内容或图片")
        
        if content_text and len(content_text) > MAX_FACADE_CONTENT_LENGTH:
            raise ValueError(f"文本内容不能超过{MAX_FACADE_CONTENT_LENGTH}字符")
        
        # 创建内容
        content = FacadeContent(
            facade_identity_id=identity.id,
            content_text=content_text,
            image_path=image_path
        )
        
        db.add(content)
        await db.commit()
        await db.refresh(content)
        
        return content
    
    async def get_gallery_contents(
        self,
        db: AsyncSession,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict]:
        """
        获取假象回廊内容列表
        
        Args:
            db: 数据库会话
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            内容列表
        """
        # 查询有效的内容
        result = await db.execute(
            select(FacadeContent, FacadeIdentity).join(
                FacadeIdentity,
                and_(
                    FacadeContent.facade_identity_id == FacadeIdentity.id,
                    FacadeIdentity.is_expired == False,
                    FacadeIdentity.expires_at > datetime.utcnow()
                )
            ).where(
                FacadeContent.is_deleted == False
            ).order_by(
                desc(FacadeContent.created_at)
            ).limit(limit).offset(offset)
        )
        
        contents = []
        for content, identity in result:
            contents.append({
                'id': content.id,
                'content_text': content.content_text,
                'image_path': content.image_path,
                'created_at': content.created_at,
                'applause_count': content.applause_count,
                'time_remaining': self._calculate_time_remaining(identity.expires_at)
            })
        
        return contents
    
    async def applaud_content(
        self,
        db: AsyncSession,
        content_id: int,
        applauder_ip: str
    ) -> bool:
        """
        为内容鼓掌
        
        Args:
            db: 数据库会话
            content_id: 内容ID
            applauder_ip: 鼓掌者IP
            
        Returns:
            是否成功鼓掌
            
        Raises:
            ValueError: 如果内容不存在或已达到鼓掌上限
        """
        # 查找内容
        result = await db.execute(
            select(FacadeContent).where(
                and_(
                    FacadeContent.id == content_id,
                    FacadeContent.is_deleted == False
                )
            )
        )
        content = result.scalar_one_or_none()
        
        if not content:
            raise ValueError("内容不存在")
        
        if content.applause_count >= MAX_APPLAUSE_PER_CONTENT:
            raise ValueError("鼓掌数已达上限")
        
        # 检查是否已经鼓掌过
        applauder_ip_hash = hash_ip(applauder_ip)
        existing_applause = await db.execute(
            select(FacadeApplause).where(
                and_(
                    FacadeApplause.content_id == content_id,
                    FacadeApplause.applauder_ip_hash == applauder_ip_hash
                )
            )
        )
        
        if existing_applause.scalar_one_or_none():
            return False  # 已经鼓掌过
        
        # 创建鼓掌记录
        applause = FacadeApplause(
            content_id=content_id,
            applauder_ip_hash=applauder_ip_hash
        )
        
        # 增加鼓掌数
        content.applause_count += 1
        
        db.add(applause)
        await db.commit()
        
        return True
    
    async def cleanup_expired_identities(self, db: AsyncSession) -> int:
        """
        清理过期的假象身份
        
        Args:
            db: 数据库会话
            
        Returns:
            清理的身份数量
        """
        current_time = datetime.utcnow()
        
        # 查找过期的身份
        result = await db.execute(
            select(FacadeIdentity).where(
                and_(
                    FacadeIdentity.expires_at <= current_time,
                    FacadeIdentity.is_expired == False
                )
            )
        )
        expired_identities = result.scalars().all()
        
        count = 0
        for identity in expired_identities:
            identity.is_expired = True
            count += 1
        
        await db.commit()
        return count
    
    def _calculate_time_remaining(self, expires_at: datetime) -> str:
        """
        计算剩余时间
        
        Args:
            expires_at: 过期时间
            
        Returns:
            剩余时间描述
        """
        remaining = expires_at - datetime.utcnow()
        
        if remaining.total_seconds() <= 0:
            return "已过期"
        
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        
        if hours > 0:
            return f"{hours}小时{minutes}分钟"
        else:
            return f"{minutes}分钟"

# 全局服务实例
facade_service = FacadeGalleryService()
