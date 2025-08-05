"""
时光信笺服务模块
"""
import json
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from ..models import TimeCapsuleLetter
from ..encryption import encryption_service, hash_ip
from ..config import MAX_LETTER_LENGTH, MAX_FUTURE_DAYS

class TimeCapsuleService:
    """时光信笺服务类"""
    
    async def create_letter(
        self,
        db: AsyncSession,
        content: str,
        title: Optional[str],
        open_date: datetime,
        send_to_void: bool = False,
        creator_ip: Optional[str] = None
    ) -> TimeCapsuleLetter:
        """
        创建时光信笺
        
        Args:
            db: 数据库会话
            content: 信笺内容
            title: 信笺标题（可选）
            open_date: 开启日期
            send_to_void: 是否寄往虚空
            creator_ip: 创建者IP
            
        Returns:
            创建的信笺对象
            
        Raises:
            ValueError: 如果参数无效
        """
        # 验证内容长度
        if len(content) > MAX_LETTER_LENGTH:
            raise ValueError(f"信笺内容不能超过{MAX_LETTER_LENGTH}字符")
        
        # 验证开启日期
        if not send_to_void:
            max_date = datetime.utcnow() + timedelta(days=MAX_FUTURE_DAYS)
            if open_date > max_date:
                raise ValueError(f"开启日期不能超过{MAX_FUTURE_DAYS}天后")
            
            if open_date <= datetime.utcnow():
                raise ValueError("开启日期必须是未来时间")
        
        # 加密内容
        encrypted_content = encryption_service.encrypt_content(content, open_date)

        # 加密标题（如果有）
        encrypted_title = None
        if title:
            encrypted_title = encryption_service.encrypt_content(title, open_date)
        
        # 创建信笺记录
        letter = TimeCapsuleLetter(
            encrypted_content=encrypted_content,
            encrypted_title=encrypted_title,
            open_at=open_date,
            send_to_void=send_to_void,
            creator_ip_hash=hash_ip(creator_ip) if creator_ip else None
        )
        
        # 如果是寄往虚空，立即标记为销毁
        if send_to_void:
            letter.is_destroyed = True
            letter.destroyed_at = datetime.utcnow()
        
        db.add(letter)
        await db.commit()
        await db.refresh(letter)
        
        return letter
    
    async def open_letter(
        self,
        db: AsyncSession,
        letter_id: int
    ) -> dict:
        """
        开启时光信笺
        
        Args:
            db: 数据库会话
            letter_id: 信笺ID
            
        Returns:
            包含解密内容的字典
            
        Raises:
            ValueError: 如果信笺不存在或无法开启
        """
        # 查找信笺
        result = await db.execute(
            select(TimeCapsuleLetter).where(TimeCapsuleLetter.id == letter_id)
        )
        letter = result.scalar_one_or_none()
        
        if not letter:
            raise ValueError("信笺不存在")
        
        if letter.is_destroyed:
            raise ValueError("信笺已被销毁")
        
        if not letter.can_be_opened():
            raise ValueError("信笺尚未到开启时间")
        
        # 解密内容
        try:
            content = encryption_service.decrypt_content(
                letter.encrypted_content,
                letter.open_at
            )

            title = None
            if letter.encrypted_title:
                title = encryption_service.decrypt_content(
                    letter.encrypted_title,
                    letter.open_at
                )
            
            # 标记为已开启
            letter.is_opened = True
            await db.commit()
            
            return {
                'id': letter.id,
                'title': title,
                'content': content,
                'created_at': letter.created_at,
                'opened_at': datetime.utcnow()
            }
        except Exception as e:
            raise ValueError(f"解密失败: {str(e)}")
    
    async def get_openable_letters(self, db: AsyncSession) -> List[TimeCapsuleLetter]:
        """
        获取可以开启的信笺列表
        
        Args:
            db: 数据库会话
            
        Returns:
            可开启的信笺列表
        """
        current_time = datetime.utcnow()
        result = await db.execute(
            select(TimeCapsuleLetter).where(
                and_(
                    TimeCapsuleLetter.open_at <= current_time,
                    TimeCapsuleLetter.is_opened == False,
                    TimeCapsuleLetter.is_destroyed == False,
                    TimeCapsuleLetter.send_to_void == False
                )
            )
        )
        return result.scalars().all()
    
    async def destroy_void_letters(self, db: AsyncSession) -> int:
        """
        销毁寄往虚空的信笺
        
        Args:
            db: 数据库会话
            
        Returns:
            销毁的信笺数量
        """
        result = await db.execute(
            select(TimeCapsuleLetter).where(
                and_(
                    TimeCapsuleLetter.send_to_void == True,
                    TimeCapsuleLetter.is_destroyed == False
                )
            )
        )
        letters = result.scalars().all()
        
        count = 0
        for letter in letters:
            letter.is_destroyed = True
            letter.destroyed_at = datetime.utcnow()
            count += 1
        
        await db.commit()
        return count

# 全局服务实例
time_capsule_service = TimeCapsuleService()
