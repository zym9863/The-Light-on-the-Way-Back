[English](README_EN.md) | [中文](README.md)

# 归途的光 - The Light on the Way Back

一个诗意的情感表达平台，包含时光信笺和假象回廊两大核心功能。

## 项目简介

"归途的光"是一个基于FastAPI和现代Web技术构建的情感表达平台，旨在为用户提供一个安全、私密且富有诗意的空间来表达内心的声音。

### 核心功能

#### 🕰️ 时光信笺 (Time Capsule Letter)
- **功能描述**: 用户可以创建一个"时光信笺"，这封信可以是一段独白、一个愿望、一个秘密，或是一句无法说出口的谎言
- **加密封存**: 在指定的开启日期之前，信笺将被加密封存，任何人都无法读取
- **寄往虚空**: 可以选择"寄往虚空"，即在创建后被立即销毁，作为一种纯粹的情感宣泄
- **定时开启**: 到达指定时间后，信笺将自动可以被开启

#### 🎭 假象回廊 (Façade Gallery)
- **功能描述**: 一个匿名的公共空间，用户可以创建临时的、完全匿名的"假象"身份
- **24小时生命周期**: 假象身份只存在24小时，体现"天一亮 我们又人模狗样"的主题
- **匿名互动**: 用户可以发布文字内容，其他用户可以进行匿名的"鼓掌"互动
- **无追踪设计**: 没有关注功能，没有长期追踪，只有短暂的真实表达

## 技术栈

- **后端框架**: FastAPI
- **包管理器**: uv
- **模板引擎**: Jinja2
- **数据库**: SQLite (使用 SQLAlchemy ORM)
- **加密**: cryptography
- **定时任务**: APScheduler
- **前端**: HTML + CSS + JavaScript (原生)

## 项目结构

```
The Light on the Way Back/
├── the_light_on_the_way_back/          # 主应用包
│   ├── __init__.py
│   ├── app.py                          # FastAPI应用主文件
│   ├── config.py                       # 配置文件
│   ├── database.py                     # 数据库连接和会话管理
│   ├── models.py                       # 数据库模型
│   ├── encryption.py                   # 加密服务
│   ├── scheduler.py                    # 定时任务调度器
│   ├── routers/                        # 路由模块
│   │   ├── __init__.py
│   │   ├── main.py                     # 主页路由
│   │   ├── time_capsule.py             # 时光信笺路由
│   │   └── facade_gallery.py           # 假象回廊路由
│   └── services/                       # 业务逻辑服务
│       ├── __init__.py
│       ├── time_capsule.py             # 时光信笺服务
│       └── facade_gallery.py           # 假象回廊服务
├── templates/                          # Jinja2模板
│   ├── base.html                       # 基础模板
│   ├── index.html                      # 首页
│   ├── time_capsule.html               # 时光信笺页面
│   └── facade_gallery.html             # 假象回廊页面
├── data/                               # 数据目录
│   └── app.db                          # SQLite数据库文件
├── main.py                             # 应用入口
├── start_server.py                     # 服务器启动脚本
├── test_app.py                         # 测试脚本
├── pyproject.toml                      # 项目配置
└── README.md                           # 项目说明
```

## 安装和运行

### 环境要求
- Python 3.12+
- uv 包管理器

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/zym9863/the-light-on-the-way-back.git
cd "The Light on the Way Back"
```

2. 安装依赖
```bash
uv sync
```

3. 运行测试
```bash
uv run python test_app.py
```

4. 启动服务器
```bash
uv run python start_server.py
```

5. 访问应用
打开浏览器访问 `http://localhost:8000`

## 功能特性

### 安全性
- 时光信笺使用基于时间的加密算法，确保在指定时间前无法解密
- IP地址哈希化处理，保护用户隐私的同时防止滥用
- 匿名身份系统，无法追踪用户真实身份

### 诗意设计
- 界面设计体现诗意美感，使用渐变色彩和柔和的视觉效果
- 功能命名富有诗意："时光信笺"、"假象回廊"、"寄往虚空"
- 交互设计注重情感表达，如"鼓掌"而非"点赞"

### 定时任务
- 自动清理过期的假象身份
- 自动销毁"寄往虚空"的信笺
- 定期检查可开启的时光信笺

## API 端点

### 主要路由
- `GET /` - 首页
- `GET /time-capsule` - 时光信笺页面
- `POST /time-capsule/create` - 创建时光信笺
- `POST /time-capsule/open/{letter_id}` - 开启时光信笺
- `GET /facade-gallery` - 假象回廊页面
- `POST /facade-gallery/create-identity` - 创建假象身份
- `POST /facade-gallery/create-content` - 创建回廊内容
- `POST /facade-gallery/applaud/{content_id}` - 为内容鼓掌
- `GET /health` - 健康检查

## 配置说明

主要配置项在 `the_light_on_the_way_back/config.py` 中：

- `DATABASE_URL`: 数据库连接URL
- `SECRET_KEY`: 应用密钥
- `ENCRYPTION_KEY`: 加密密钥
- `MAX_LETTER_LENGTH`: 最大信笺长度
- `FACADE_LIFETIME_HOURS`: 假象身份存在时间

## 开发说明

### 添加新功能
1. 在 `models.py` 中定义数据模型
2. 在 `services/` 中实现业务逻辑
3. 在 `routers/` 中添加API路由
4. 在 `templates/` 中创建前端模板

### 测试
运行 `test_app.py` 进行基本功能测试，包括：
- 加密/解密功能测试
- 时光信笺创建和开启测试
- 假象回廊功能测试

## 许可证

本项目采用 MIT 许可证。

## 致谢

感谢所有为这个项目贡献想法和代码的人。愿每个人都能在"归途的光"中找到属于自己的那份宁静与真实。

---

*"纸一张 字一脏 藏着我无畏的模样"*
*"天一亮 我们又人模狗样"*