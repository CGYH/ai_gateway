"""POST /v1/chat/completions：网关的核心转发端点。

M0 转发链（刻意保持最短）：网关鉴权 → 模型名固定映射到 .env 上游 → 流式/非流式转发。
M1 起在中间插入：路由 → 渠道选择 → 配额检查 → 失败重试 → 记账。
"""
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse

from app.config import get_settings
from app.providers import openai_compat

router = APIRouter(prefix="/v1")


def _error(status: int, message: str, err_type: str) -> JSONResponse:
    """按 OpenAI 的错误格式返回，客户端才能正确解析显示。"""
    return JSONResponse(status_code=status, content={"error": {"message": message, "type": err_type}})


@router.post("/chat/completions")
async def chat_completions(request: Request):
    settings = get_settings()

    # 1. 网关自身鉴权：客户端拿的是我们自发 key，不是任何厂商的 key
    auth = request.headers.get("authorization", "")
    if auth != f"Bearer {settings.gateway_api_key}":
        return _error(401, "invalid gateway key（检查客户端里填的网关 key）", "auth_error")

    # 2. 上游是否已配置
    if not (settings.upstream_base_url and settings.upstream_api_key and settings.upstream_model):
        return _error(503, "upstream not configured: 请填写 .env 的 UPSTREAM_* 三项", "config_error")

    # 3. 解析请求体；M0 阶段模型名固定映射到配置的上游模型（M1 起由路由器接管）
    try:
        payload = await request.json()
    except Exception:
        return _error(400, "request body is not valid JSON", "invalid_request")
    payload["model"] = settings.upstream_model
    payload["stream"] = bool(payload.get("stream", False))

    # 4. 转发：流式走 SSE 逐块透传；非流式走 JSON 透传
    if payload["stream"]:
        return StreamingResponse(
            openai_compat.stream_chat(payload, settings),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    try:
        resp = await openai_compat.forward_chat(payload, settings)
    except httpx.ConnectError as exc:
        return _error(502, f"cannot reach upstream: {exc}", "upstream_error")
    except httpx.HTTPError as exc:
        return _error(502, f"upstream transport error: {exc}", "upstream_error")
    try:
        body = resp.json()
    except Exception:
        body = {"raw": resp.text}
    return JSONResponse(status_code=resp.status_code, content=body)
