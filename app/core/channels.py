"""渠道（Channel）数据模型：整个网关的核心抽象。

一个渠道 = 一个厂商端点 + 一把 key + 能力标签 + 配额规则。
你那几个英伟达账号，就是同一 base_url 下的 N 个渠道（M1 起入库 SQLite）。
"""
from pydantic import BaseModel, Field


class QuotaRule(BaseModel):
    """单条配额规则；一个渠道挂多条，规则间 AND 组合，任一触顶即临时摘除渠道。

    例：
      英伟达免费账号 → QuotaRule(dimension="calls",  window="rolling:60m",   limit=40)
      按次计费日重置 → QuotaRule(dimension="calls",  window="calendar_day",  limit=500)
      token 窗口限制 → QuotaRule(dimension="tokens", window="rolling:60m",   limit=100_000)
    """

    dimension: str = Field(description="计量维度：calls | tokens | images")
    window: str = Field(description="窗口类型：rolling:<N>m | calendar_day | calendar_month")
    limit: int = Field(gt=0, description="窗口内允许的上限")


class Channel(BaseModel):
    """渠道定义。api_key 一律 repr 脱敏，日志里不能出现完整密钥。"""

    id: int | None = None
    name: str
    base_url: str
    api_key: str = Field(repr=False)
    capabilities: set[str] = Field(
        default_factory=set,
        description="能力标签：chat | embeddings | images | vision",
    )
    models: list[str] = Field(default_factory=list, description="可服务的模型 id / 别名")
    priority: int = Field(default=100, description="数值越小越优先；免费池给小值")
    quota_rules: list[QuotaRule] = Field(default_factory=list)
    enabled: bool = True
