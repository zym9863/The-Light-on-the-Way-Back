"""
FastAPI应用主文件
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import init_db
from .routers import main_router, time_capsule_router, facade_gallery_router
from .config import APP_NAME, APP_DESCRIPTION, VERSION, STATIC_DIR
from .scheduler import start_scheduler, stop_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    # 启动定时任务调度器
    await start_scheduler()
    yield
    # 关闭时的清理工作
    await stop_scheduler()

# 创建FastAPI应用
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=VERSION,
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# 注册路由
app.include_router(main_router)
app.include_router(time_capsule_router)
app.include_router(facade_gallery_router)

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "app": APP_NAME, "version": VERSION}
