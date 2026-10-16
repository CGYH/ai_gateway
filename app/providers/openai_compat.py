"""OpenAI 兼容上游的转发实现（M0）。

核心原则：流式请求必须「收到一块就吐一块」（aiter_bytes 逐块透传），
绝不能读完整响应再返回 —— 那会让客户端干等到最后才一次性出字。
M1 记账时会把「原始字节透传」升级为「按行解析」，以便提取 usage。
"""
import json

import httpx

from app.config import Settings

# LLM 生成期间上游可能长时间不结束：read 超时必须放宽，连接超时保持敏感
TIMEOUT = httpx.Timeout(connect=15.0, read=300.0, write=60.0, pool=300.0)


def _auth_headers(settings: Settings) -> dict:
    return {"Authorization": f"Bearer {settings.upstream_api_key}"}


async def forward_chat(payload: dict, settings: Settings) -> httpx.Response:
    """非流式转发：返回已读完 body 的 httpx.Response。"""
    async with httpx.AsyncClient(base_url=settings.upstream_base_url, timeout=TIMEOUT) as client:
        return await client.post("/chat/completions", json=payload, headers=_auth_headers(settings))


async def stream_chat(payload: dict, settings: Settings):
    """流式转发：异步生成器，把上游 SSE 字节原样逐块 yield 给调用方。

    上游报错时降级为一条 data: 错误事件 + [DONE]，保证客户端能收到可读原因，
    而不是挂着连接干等。
    """
    async with httpx.AsyncClient(base_url=settings.upstream_base_url, timeout=TIMEOUT) as client:
        async with client.stream(
            "POST", "/chat/completions", json=payload, headers=_auth_headers(settings)
        ) as resp:
            if resp.status_code >= 400:
                body = (await resp.aread()).decode("utf-8", errors="replace")
                err = {"error": {"message": f"upstream {resp.status_code}: {body}", "type": "upstream_error"}}
                yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
                return
            async for chunk in resp.aiter_bytes():
                yield chunk
