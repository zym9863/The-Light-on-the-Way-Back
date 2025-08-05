"""
时光信笺路由
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..services import time_capsule_service
from ..config import TEMPLATES_DIR

router = APIRouter(prefix="/time-capsule", tags=["time-capsule"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("/")
async def time_capsule_page(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """时光信笺页面"""
    # 获取可开启的信笺
    openable_letters = await time_capsule_service.get_openable_letters(db)
    
    return templates.TemplateResponse(
        "time_capsule.html",
        {
            "request": request,
            "openable_letters": openable_letters
        }
    )

@router.post("/create")
async def create_letter(
    request: Request,
    title: Optional[str] = Form(None),
    content: str = Form(...),
    open_date: Optional[str] = Form(None),
    send_to_void: bool = Form(False),
    db: AsyncSession = Depends(get_db)
):
    """创建时光信笺"""
    try:
        # 获取客户端IP
        client_ip = request.client.host
        
        # 处理开启日期
        open_datetime = None
        if not send_to_void and open_date:
            try:
                open_datetime = datetime.fromisoformat(open_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="日期格式无效")
        elif not send_to_void:
            raise HTTPException(status_code=400, detail="必须指定开启日期")
        else:
            # 寄往虚空的信笺，设置一个默认的未来时间（不会被使用）
            open_datetime = datetime.utcnow()
        
        # 创建信笺
        letter = await time_capsule_service.create_letter(
            db=db,
            content=content,
            title=title,
            open_date=open_datetime,
            send_to_void=send_to_void,
            creator_ip=client_ip
        )
        
        if send_to_void:
            message = "信笺已寄往虚空，愿你的心绪得到释放"
        else:
            message = f"信笺已封存，将在 {open_datetime.strftime('%Y年%m月%d日 %H:%M')} 开启"
        
        return templates.TemplateResponse(
            "time_capsule.html",
            {
                "request": request,
                "success_message": message,
                "openable_letters": await time_capsule_service.get_openable_letters(db)
            }
        )
        
    except ValueError as e:
        return templates.TemplateResponse(
            "time_capsule.html",
            {
                "request": request,
                "error_message": str(e),
                "openable_letters": await time_capsule_service.get_openable_letters(db)
            }
        )

@router.post("/open/{letter_id}")
async def open_letter(
    letter_id: int,
    db: AsyncSession = Depends(get_db)
):
    """开启时光信笺"""
    try:
        letter_data = await time_capsule_service.open_letter(db, letter_id)
        return JSONResponse(content=letter_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
