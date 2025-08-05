"""
定时任务调度器
"""
import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from .database import AsyncSessionLocal
from .services import time_capsule_service, facade_service

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskScheduler:
    """定时任务调度器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """设置定时任务"""
        # 每小时清理过期的假象身份
        self.scheduler.add_job(
            self.cleanup_expired_identities,
            trigger=IntervalTrigger(hours=1),
            id="cleanup_expired_identities",
            name="清理过期假象身份",
            replace_existing=True
        )
        
        # 每天清理寄往虚空的信笺
        self.scheduler.add_job(
            self.cleanup_void_letters,
            trigger=IntervalTrigger(hours=24),
            id="cleanup_void_letters",
            name="清理虚空信笺",
            replace_existing=True
        )
        
        # 每分钟检查可开启的信笺（用于通知等功能）
        self.scheduler.add_job(
            self.check_openable_letters,
            trigger=IntervalTrigger(minutes=1),
            id="check_openable_letters",
            name="检查可开启信笺",
            replace_existing=True
        )
    
    async def cleanup_expired_identities(self):
        """清理过期的假象身份"""
        try:
            async with AsyncSessionLocal() as db:
                count = await facade_service.cleanup_expired_identities(db)
                if count > 0:
                    logger.info(f"清理了 {count} 个过期的假象身份")
        except Exception as e:
            logger.error(f"清理过期假象身份时出错: {e}")
    
    async def cleanup_void_letters(self):
        """清理寄往虚空的信笺"""
        try:
            async with AsyncSessionLocal() as db:
                count = await time_capsule_service.destroy_void_letters(db)
                if count > 0:
                    logger.info(f"清理了 {count} 封虚空信笺")
        except Exception as e:
            logger.error(f"清理虚空信笺时出错: {e}")
    
    async def check_openable_letters(self):
        """检查可开启的信笺"""
        try:
            async with AsyncSessionLocal() as db:
                letters = await time_capsule_service.get_openable_letters(db)
                if letters:
                    logger.info(f"发现 {len(letters)} 封可开启的信笺")
                    # 这里可以添加通知逻辑，比如发送邮件、推送等
        except Exception as e:
            logger.error(f"检查可开启信笺时出错: {e}")
    
    def start(self):
        """启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("定时任务调度器已启动")
    
    def shutdown(self):
        """关闭调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("定时任务调度器已关闭")

# 全局调度器实例
scheduler = TaskScheduler()

async def start_scheduler():
    """启动调度器（异步）"""
    scheduler.start()

async def stop_scheduler():
    """停止调度器（异步）"""
    scheduler.shutdown()
