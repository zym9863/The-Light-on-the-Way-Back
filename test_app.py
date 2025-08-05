"""
简单的应用测试
"""
import asyncio
from datetime import datetime, timedelta
from the_light_on_the_way_back.database import init_db, AsyncSessionLocal
from the_light_on_the_way_back.services import time_capsule_service, facade_service
from the_light_on_the_way_back.encryption import encryption_service

async def test_encryption():
    """测试加密功能"""
    print("测试加密功能...")
    
    content = "这是一个测试信笺的内容"
    open_date = datetime.utcnow() + timedelta(seconds=5)  # 5秒后开启
    
    # 加密
    encrypted_data = encryption_service.encrypt_content(content, open_date)
    print(f"内容已加密，长度: {len(encrypted_data)} 字节")
    
    # 尝试提前解密（应该失败）
    try:
        decrypted = encryption_service.decrypt_content(encrypted_data, open_date, datetime.utcnow())
        print("错误：提前解密成功了！")
    except ValueError as e:
        print(f"正确：提前解密失败 - {e}")
    
    # 等待5秒
    print("等待5秒...")
    await asyncio.sleep(5)
    
    # 现在应该可以解密
    try:
        decrypted = encryption_service.decrypt_content(encrypted_data, open_date, datetime.utcnow())
        print(f"解密成功: {decrypted}")
    except ValueError as e:
        print(f"解密失败: {e}")

async def test_time_capsule():
    """测试时光信笺功能"""
    print("\n测试时光信笺功能...")
    
    async with AsyncSessionLocal() as db:
        # 创建一个立即可开启的信笺
        open_date = datetime.utcnow() + timedelta(seconds=1)
        
        letter = await time_capsule_service.create_letter(
            db=db,
            content="这是一个测试信笺",
            title="测试标题",
            open_date=open_date,
            send_to_void=False,
            creator_ip="127.0.0.1"
        )
        
        print(f"信笺已创建，ID: {letter.id}")
        
        # 等待1秒
        await asyncio.sleep(1)
        
        # 尝试开启
        try:
            letter_data = await time_capsule_service.open_letter(db, letter.id)
            print(f"信笺开启成功: {letter_data}")
        except ValueError as e:
            print(f"信笺开启失败: {e}")

async def test_facade_gallery():
    """测试假象回廊功能"""
    print("\n测试假象回廊功能...")
    
    async with AsyncSessionLocal() as db:
        # 创建假象身份
        identity = await facade_service.create_identity(db, "127.0.0.1")
        print(f"假象身份已创建: {identity.identity_token}")
        
        # 创建内容
        content = await facade_service.create_content(
            db=db,
            identity_token=identity.identity_token,
            content_text="这是一个测试内容"
        )
        print(f"内容已创建，ID: {content.id}")
        
        # 获取回廊内容
        contents = await facade_service.get_gallery_contents(db, limit=10)
        print(f"回廊中有 {len(contents)} 个内容")
        
        # 鼓掌
        success = await facade_service.applaud_content(db, content.id, "192.168.1.1")
        print(f"鼓掌{'成功' if success else '失败'}")

async def main():
    """主测试函数"""
    print("开始测试归途的光应用...")
    
    # 初始化数据库
    await init_db()
    print("数据库初始化完成")
    
    # 运行测试
    await test_encryption()
    await test_time_capsule()
    await test_facade_gallery()
    
    print("\n所有测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
