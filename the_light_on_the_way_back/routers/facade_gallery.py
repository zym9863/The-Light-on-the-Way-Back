"""
假象回廊路由
"""
from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, HTTPException, Query, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..services import facade_service
from ..config import TEMPLATES_DIR

router = APIRouter(prefix="/facade-gallery", tags=["facade-gallery"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("/")
async def facade_gallery_page(
    request: Request,
    identity_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    """假象回廊页面"""
    # 验证身份令牌
    identity = None
    time_remaining = None
    
    if identity_token:
        identity = await facade_service.get_identity(db, identity_token)
        if identity and identity.is_valid():
            time_remaining = facade_service._calculate_time_remaining(identity.expires_at)
        else:
            identity_token = None
    
    # 获取回廊内容
    contents = await facade_service.get_gallery_contents(db, limit=20)
    
    return templates.TemplateResponse(
        "facade_gallery.html",
        {
            "request": request,
            "identity_token": identity_token,
            "time_remaining": time_remaining,
            "contents": contents
        }
    )

@router.post("/create-identity")
async def create_identity(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """创建假象身份"""
    try:
        # 获取客户端IP
        client_ip = request.client.host
        
        # 创建身份
        identity = await facade_service.create_identity(db, client_ip)
        
        # 设置Cookie并重定向
        response = RedirectResponse(url="/facade-gallery", status_code=302)
        response.set_cookie(
            key="identity_token",
            value=identity.identity_token,
            max_age=24 * 60 * 60,  # 24小时
            httponly=True,
            secure=False  # 在生产环境中应设为True
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建身份失败: {str(e)}")

@router.post("/create-content")
async def create_content(
    request: Request,
    identity_token: str = Form(...),
    content_text: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """创建假象回廊内容"""
    try:
        # 创建内容
        content = await facade_service.create_content(
            db=db,
            identity_token=identity_token,
            content_text=content_text
        )
        
        return RedirectResponse(url="/facade-gallery", status_code=302)
        
    except ValueError as e:
        # 返回错误页面
        contents = await facade_service.get_gallery_contents(db, limit=20)
        identity = await facade_service.get_identity(db, identity_token)
        time_remaining = facade_service._calculate_time_remaining(identity.expires_at) if identity else None
        
        return templates.TemplateResponse(
            "facade_gallery.html",
            {
                "request": request,
                "identity_token": identity_token,
                "time_remaining": time_remaining,
                "contents": contents,
                "error_message": str(e)
            }
        )

@router.post("/applaud/{content_id}")
async def applaud_content(
    content_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """为内容鼓掌"""
    try:
        # 获取客户端IP
        client_ip = request.client.host
        
        # 鼓掌
        success = await facade_service.applaud_content(db, content_id, client_ip)
        
        if success:
            # 获取更新后的鼓掌数
            contents = await facade_service.get_gallery_contents(db, limit=1000)
            content = next((c for c in contents if c['id'] == content_id), None)
            
            return JSONResponse(content={
                "success": True,
                "applause_count": content['applause_count'] if content else 0
            })
        else:
            raise HTTPException(status_code=400, detail="你已经为这个内容鼓掌过了")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/contents")
async def get_contents(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """获取回廊内容（API）"""
    contents = await facade_service.get_gallery_contents(db, limit=limit, offset=offset)
    return JSONResponse(content={"contents": contents})
