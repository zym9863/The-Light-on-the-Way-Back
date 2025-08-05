"""
路由模块
"""
from .time_capsule import router as time_capsule_router
from .facade_gallery import router as facade_gallery_router
from .main import router as main_router

__all__ = ['time_capsule_router', 'facade_gallery_router', 'main_router']
