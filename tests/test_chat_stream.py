"""M0 集成测试：真实上游的流式转发。

.env 未配置 UPSTREAM_* 时自动跳过（保证任何人 clone 下来 pytest 都能跑）；
配置了就打一次真实请求，max_tokens 压到 32，几乎不消耗额度。
"""
import json

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app

settings = get_settings()
needs_upstream = pytest.mark.skipif(
    not (settings.upstream_base_url and settings.upstream_api_key and settings.upstream_model),
    reason=".env 未配置 UPSTREAM_*",
)


@needs_upstream
def test_chat_stream_arrives_in_chunks():
    """流式请求必须：200 + 多个 data 事件 + [DONE] 结尾 + 至少一个内容块。"""
    client = TestClient(app)
    with client.stream(
        "POST",
        "/v1/chat/completions",
        headers={"Authorization": f"Bearer {settings.gateway_api_key}"},
        json={
            "model": "anything-m0-maps-it-to-upstream",
            "stream": True,
            "max_tokens": 32,
            "messages": [{"role": "user", "content": "只回复两个字：你好"}],
        },
    ) as resp:
        assert resp.status_code == 200
        events = [line[len("data: "):] for line in resp.iter_lines() if line.startswith("data: ")]
    assert len(events) >= 2, f"SSE 事件太少: {events}"
    assert events[-1] == "[DONE]"
    chunks = [json.loads(e) for e in events[:-1]]
    assert any(c.get("choices") for c in chunks), f"没有内容块: {events}"


@needs_upstream
def test_chat_non_stream_json():
    """非流式请求：JSON 透传，结构完整。"""
    client = TestClient(app)
    resp = client.post(
        "/v1/chat/completions",
        headers={"Authorization": f"Bearer {settings.gateway_api_key}"},
        json={
            "model": "anything",
            "stream": False,
            "max_tokens": 16,
            "messages": [{"role": "user", "content": "只回复两个字：你好"}],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["choices"][0]["message"]["role"] == "assistant"


def test_chat_rejects_bad_gateway_key():
    """网关鉴权：错误的自发 key 必须被 401 挡住，绝不落到上游。"""
    client = TestClient(app)
    resp = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer wrong-key"},
        json={"model": "x", "messages": [{"role": "user", "content": "hi"}]},
    )
    assert resp.status_code == 401
