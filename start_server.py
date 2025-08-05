#!/usr/bin/env python3
"""
启动服务器脚本
"""
import uvicorn
import asyncio
import sys
import traceback

async def test_app():
    """测试应用是否可以正常导入和初始化"""
    try:
        print("正在导入应用...")
        from the_light_on_the_way_back.app import app
        print("应用导入成功！")

        print("正在测试数据库连接...")
        from the_light_on_the_way_back.database import init_db
        await init_db()
        print("数据库连接成功！")

        return True
    except Exception as e:
        print(f"应用初始化失败: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("正在启动归途的光服务器...")

    # 先测试应用
    if asyncio.run(test_app()):
        print("开始启动Web服务器...")
        try:
            uvicorn.run(
                "the_light_on_the_way_back.app:app",
                host="0.0.0.0",
                port=8000,
                reload=False,
                log_level="info"
            )
        except Exception as e:
            print(f"服务器启动失败: {e}")
            traceback.print_exc()
            sys.exit(1)
    else:
        print("应用初始化失败，无法启动服务器")
        sys.exit(1)
