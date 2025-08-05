"""
归途的光 - 主应用入口
"""
import uvicorn
from the_light_on_the_way_back.app import app

def main():
    """启动应用"""
    uvicorn.run(
        "the_light_on_the_way_back.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()
