"""
主页路由
"""
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from ..config import TEMPLATES_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("/")
async def index(request: Request):
    """首页"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )
