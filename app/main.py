"""应用入口：FastAPI 实例、路由挂载、健康检查。

启动方式：
    uvicorn app.main:app --reload --port 8317
"""
from fastapi import FastAPI

from app.routes import chat, models

app = FastAPI(
    title="AI Gateway",
    version="0.0.1",
    description="个人多供应商 AI 网关：配额轮换 · 故障转移 · 档位路由",
)

app.include_router(models.router)
app.include_router(chat.router)


@app.get("/healthz", tags=["meta"])
async def healthz() -> dict:
    """存活检查：面板与脚本用它判断网关是否在跑。"""
    return {"status": "ok"}
