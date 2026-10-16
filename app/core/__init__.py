"""核心业务层：渠道模型、路由器、配额引擎、记账。

这一层不碰 HTTP 细节 —— routes 层调它，它调 providers 与 db。
"""
