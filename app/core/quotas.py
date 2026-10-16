"""配额引擎：判断「此刻该渠道还能不能用」。

实现口径（M1）：
- rolling:<N>m → 对 usage_log 按时间戳 COUNT/SUM 最近 N 分钟
- calendar_day / calendar_month → 按本地时区零点重置计数

个人量级直接查 SQLite 就够，不需要内存计数器数据结构。
"""


def is_available(channel, usage_summary) -> bool:
    """逐条评估渠道的配额规则，全部通过才可用。TODO(M1)"""
    raise NotImplementedError("M1 实现")
