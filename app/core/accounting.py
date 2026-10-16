"""记账：把每次调用的用量写入 usage_log。

- 非流式：直接读响应里的 usage 字段
- 流式：请求带 include_usage 拿 usage；上游不支持时降级为字符数估算 —— 记账宁粗勿漏
- 按次计费渠道：记 calls 维度并按单价折算成本
"""


def record(channel_id: int, model: str, usage: dict) -> None:
    """TODO(M1)：写 usage_log 表。"""
    raise NotImplementedError("M1 实现")
