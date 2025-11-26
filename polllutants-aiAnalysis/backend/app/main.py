from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 兼容两种启动方式：
# 1) 作为包：uvicorn app.main:app
# 2) 作为脚本：python main.py（在 app 目录下执行）
try:  # 优先按包内相对导入（推荐方式）
    from .config import get_settings
    from .routers.analysis import router as analysis_router
except ImportError:  # 兼容直接 python main.py
    import os
    import sys

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.dirname(CURRENT_DIR)
    if PARENT_DIR not in sys.path:
        sys.path.insert(0, PARENT_DIR)

    from app.config import get_settings  # type: ignore
    from app.routers.analysis import router as analysis_router  # type: ignore


settings = get_settings()

app = FastAPI(
    title="污染物监测分析平台",
    version="0.1.0",
    description="FastAPI 后端，提供监测站点、污染物以及站点/TIF对比分析数据接口。",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router, prefix="")


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "message": "pollutants analysis api online"}