"""
数据库模型定义
"""
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, LargeBinary
from sqlalchemy.sql import func
from .database import Base

class TimeCapsuleLetter(Base):
    """时光信笺模型"""
    __tablename__ = "time_capsule_letters"
    
    id = Column(Integer, primary_key=True, index=True)
    # 加密的内容
    encrypted_content = Column(LargeBinary, nullable=False)
    # 加密的标题（可选）
    encrypted_title = Column(LargeBinary, nullable=True)
    # 创建时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # 开启时间
    open_at = Column(DateTime(timezone=True), nullable=False)
    # 是否已开启
    is_opened = Column(Boolean, default=False)
    # 是否寄往虚空（创建后立即销毁）
    send_to_void = Column(Boolean, default=False)
    # 是否已销毁
    is_destroyed = Column(Boolean, default=False)
    # 销毁时间
    destroyed_at = Column(DateTime(timezone=True), nullable=True)
    # 创建者IP（用于防滥用，不用于身份识别）
    creator_ip_hash = Column(String(64), nullable=True)
    
    def can_be_opened(self) -> bool:
        """检查是否可以开启"""
        return datetime.utcnow() >= self.open_at and not self.is_destroyed
    
    def should_be_destroyed(self) -> bool:
        """检查是否应该被销毁（寄往虚空的信笺）"""
        return self.send_to_void and not self.is_destroyed

class FacadeIdentity(Base):
    """假象身份模型"""
    __tablename__ = "facade_identities"
    
    id = Column(Integer, primary_key=True, index=True)
    # 匿名身份标识（随机生成）
    identity_token = Column(String(64), unique=True, nullable=False, index=True)
    # 创建时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # 过期时间（24小时后）
    expires_at = Column(DateTime(timezone=True), nullable=False)
    # 是否已过期
    is_expired = Column(Boolean, default=False)
    # 创建者IP哈希（防滥用）
    creator_ip_hash = Column(String(64), nullable=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(hours=24)
    
    def is_valid(self) -> bool:
        """检查身份是否有效"""
        return datetime.utcnow() < self.expires_at and not self.is_expired

class FacadeContent(Base):
    """假象回廊内容模型"""
    __tablename__ = "facade_contents"
    
    id = Column(Integer, primary_key=True, index=True)
    # 关联的假象身份ID
    facade_identity_id = Column(Integer, nullable=False, index=True)
    # 内容文本
    content_text = Column(Text, nullable=True)
    # 图片路径（如果有）
    image_path = Column(String(255), nullable=True)
    # 创建时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # 鼓掌数
    applause_count = Column(Integer, default=0)
    # 是否已删除
    is_deleted = Column(Boolean, default=False)

class FacadeApplause(Base):
    """假象回廊鼓掌记录模型"""
    __tablename__ = "facade_applause"
    
    id = Column(Integer, primary_key=True, index=True)
    # 内容ID
    content_id = Column(Integer, nullable=False, index=True)
    # 鼓掌者IP哈希（防止重复鼓掌）
    applauder_ip_hash = Column(String(64), nullable=False)
    # 鼓掌时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    class Meta:
        # 确保同一IP对同一内容只能鼓掌一次
        unique_together = [['content_id', 'applauder_ip_hash']]
