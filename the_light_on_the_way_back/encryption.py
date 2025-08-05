"""
加密服务模块
实现时光信笺的加密封存功能
"""
import base64
import hashlib
import secrets
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from .config import ENCRYPTION_KEY

class EncryptionService:
    """加密服务类"""
    
    def __init__(self, master_key: str = ENCRYPTION_KEY):
        self.master_key = master_key.encode()
    
    def _derive_key(self, salt: bytes, open_date: datetime) -> bytes:
        """
        基于盐值和开启日期派生加密密钥
        这确保了只有在指定日期后才能正确解密
        """
        # 将开启日期转换为字节
        date_bytes = open_date.isoformat().encode()
        
        # 组合主密钥、盐值和日期
        key_material = self.master_key + salt + date_bytes
        
        # 使用PBKDF2派生密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(key_material))
    
    def encrypt_content(self, content: str, open_date: datetime) -> bytes:
        """
        加密内容

        Args:
            content: 要加密的内容
            open_date: 开启日期

        Returns:
            包含盐值和加密数据的字节串
        """
        # 生成随机盐值
        salt = secrets.token_bytes(32)

        # 派生加密密钥
        key = self._derive_key(salt, open_date)

        # 创建Fernet实例
        fernet = Fernet(key)

        # 加密内容
        encrypted_content = fernet.encrypt(content.encode())

        # 将盐值和加密内容组合
        return salt + encrypted_content
    
    def decrypt_content(self, encrypted_data: bytes, open_date: datetime, current_date: datetime = None) -> str:
        """
        解密内容

        Args:
            encrypted_data: 包含盐值和加密数据的字节串
            open_date: 开启日期
            current_date: 当前日期（用于验证是否可以解密）

        Returns:
            解密后的内容

        Raises:
            ValueError: 如果还未到开启时间或解密失败
        """
        if current_date is None:
            current_date = datetime.utcnow()

        # 检查是否到了开启时间
        if current_date < open_date:
            raise ValueError("信笺尚未到开启时间")

        # 提取盐值和加密内容
        salt = encrypted_data[:32]
        encrypted_content = encrypted_data[32:]

        # 派生解密密钥
        key = self._derive_key(salt, open_date)

        # 创建Fernet实例
        fernet = Fernet(key)

        try:
            # 解密内容
            decrypted_content = fernet.decrypt(encrypted_content)
            return decrypted_content.decode()
        except Exception as e:
            raise ValueError(f"解密失败: {str(e)}")
    
    def can_decrypt(self, open_date: datetime, current_date: datetime = None) -> bool:
        """
        检查是否可以解密
        
        Args:
            open_date: 开启日期
            current_date: 当前日期
            
        Returns:
            是否可以解密
        """
        if current_date is None:
            current_date = datetime.utcnow()
        
        return current_date >= open_date

def hash_ip(ip_address: str) -> str:
    """
    对IP地址进行哈希处理，用于防滥用而不泄露真实IP
    
    Args:
        ip_address: IP地址
        
    Returns:
        哈希后的IP
    """
    return hashlib.sha256(ip_address.encode()).hexdigest()

def generate_identity_token() -> str:
    """
    生成假象身份令牌
    
    Returns:
        随机生成的身份令牌
    """
    return secrets.token_urlsafe(32)

# 全局加密服务实例
encryption_service = EncryptionService()
