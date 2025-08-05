"""
应用配置模块
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/data/app.db")

# 安全配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 加密配置
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "your-encryption-key-change-in-production")

# 应用配置
APP_NAME = "归途的光"
APP_DESCRIPTION = "一个诗意的情感表达平台"
VERSION = "0.1.0"

# 时光信笺配置
MAX_LETTER_LENGTH = 5000  # 最大信笺长度
MAX_FUTURE_DAYS = 365 * 5  # 最多可设置5年后开启

# 假象回廊配置
FACADE_LIFETIME_HOURS = 24  # 假象身份存在时间（小时）
MAX_FACADE_CONTENT_LENGTH = 1000  # 最大内容长度
MAX_APPLAUSE_PER_CONTENT = 100  # 每个内容最多鼓掌数

# 静态文件配置
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# 确保模板目录存在
TEMPLATES_DIR.mkdir(exist_ok=True)

# 确保数据目录存在
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
