"""GET /v1/models：向客户端公布逻辑模型列表。

DSH 的 pi-ai 适配器、Cherry Studio 等客户端靠这个端点做模型发现；
M1 起从渠道配置聚合生成，并做模型别名归一。
"""
from fastapi import APIRouter

router = APIRouter(prefix="/v1")


@router.get("/models")
async def list_models() -> dict:
    # TODO(M1): 聚合所有启用渠道的模型列表 + 别名归一
    return {"object": "list", "data": []}
