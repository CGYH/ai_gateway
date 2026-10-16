"""POST /v1/chat/completions：网关的核心转发端点。

M0 目标：请求原样转发到单一上游，SSE 逐块回传 —— 先打死全项目最大的技术风险。
M1 起转发链变成：认证 → 路由 → 渠道选择 → 配额检查 → 转发 → 失败重试 → 记账。
"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/v1")


@router.post("/chat/completions")
async def chat_completions(request: Request) -> JSONResponse:
    # TODO(M0): providers 层实现 httpx 流式转发 + SSE 透传
    return JSONResponse(
        status_code=501,
        content={
            "error": {
                "message": "M0 尚未实现：这里是流式转发的落点",
                "type": "not_implemented",
            }
        },
    )
