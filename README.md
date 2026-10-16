# AI Gateway（个人多供应商 AI 网关）

把散落各处的 API——英伟达免费账号 ×N、DeepSeek 官方、各家 OpenAI 兼容中转——聚合成
**一个 OpenAI 兼容入口**（`http://127.0.0.1:8317/v1`），由网关负责：

- **配额轮换**：滚动窗口 RPM/TPM、自然日重置按次计费、token 预算……任一规则触顶自动摘除渠道
- **故障转移**：429/5xx 自动冷却并换下一个渠道重试
- **档位路由**（M3）：经济 / 均衡 / 强力三档 + 规则启发式升降档，手动指定永远优先
- **记账与成本**：按渠道记录 token / 次数 / 花费，面板可视化（M2）

## 架构

```
客户端（Cherry Studio / DSH / 脚本）
        │  http://127.0.0.1:8317/v1 + 网关自发 key
        ▼
┌──────────────────────────────────┐
│ FastAPI 网关                      │
│  routes/   对外端点（chat/models）│
│  core/     路由 · 配额 · 渠道 · 记账│
│  providers/上游转发（httpx 流式）  │
│  db        SQLite（单文件）       │
└──────────────────────────────────┘
        ▼
  英伟达×N / DeepSeek / 中转站 / ...
```

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # 若报执行策略错误：Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
pip install -e ".[dev]"
copy .env.example .env              # 然后编辑 .env 填入真实 key
uvicorn app.main:app --reload --port 8317
pytest                              # 另开一个终端跑冒烟测试
```

## 里程碑

| 里程碑 | 内容 | 状态 |
|---|---|---|
| M0 | 单上游流式转发技术验证（SSE 透传） | ⬜ |
| M1 | 多渠道 + 轮换 + 配额规则 + 记账 | ⬜ |
| M2 | 控制面板（渠道管理 / 用量仪表） | ⬜ |
| M3 | 档位 + 规则启发式路由 | ⬜ |
| M4 | Anthropic 协议端点 / 文生图与 embeddings 转发线 / 导入导出 | ⬜ |

## 关键设计约定

- **渠道（Channel）是核心抽象**：一个厂商端点 + 一把 key + 能力标签（`chat/embeddings/images/vision`）+ 配额规则列表。同一厂商的 N 个账号 = N 个渠道。
- **配额规则 AND 组合**：维度（次数/token/图片数）× 窗口（滚动 N 分钟 / 自然日 / 自然月），任一触顶即临时摘除渠道。
- **embedding 模型锁定**：不同 embedding 模型的向量互不兼容，只允许在"同模型的不同渠道"间轮换。
- **密钥永不入库（git 意义上的库）**：`.env` 与 SQLite 均被 `.gitignore` 排除，日志一律脱敏。
