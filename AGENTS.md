# 九歌 (Jiǔ Gē) — 项目规则

> 继承自全局约束体系（S01-S11、六原则、控制论卡）。
> 以下为九歌项目专属补充规则。

---

## 目录结构

```
JiuGe/
├── README.md             ← 用户文档
├── AGENTS.md             ← AI 行为指南
├── servers/              ← 各 MCP server
│   ├── podcast/
│   ├── wechat/
│   ├── bilibili/
│   ├── research/
│   └── textbook/         ← 互动教材生成器 (新增)
├── frontend/             ← 管理界面 (新增，从总经办 dashboard 拆出)
├── core/                 ← 共享基础设施
├── tests/
└── data/                 ← 缓存
```

## MCP 开发规则

- 每台 server 独立可部署、可卸载
- 优先用 Python MCP SDK
- LLM 调用优先走 env var 中的 API key，fallback 到 Ollama
- core/ 中的基础设施不做泛化抽象，只做当前够用

## textbook server 专项规则

- 输入源：CCBrain/deep_dives/ 中的深度分析 Markdown 文件
- 输出：符合 Luffa SuperBox schema 的互动内容 JSON
- 生成流程：读文件 → LLM 提取关键概念 → 生成互动模块（模拟器/问答/对比）
- 依赖 chain：call_llm_chain（可复用总经办 llm_caller，或独立实现）

## 跨项目依赖

- `servers/textbook/` 对 总经办 项目（`C:/Users/Augfoto ASUS/Documents/deepseek/`）的依赖：
  - 只读：`CCBrain/deep_dives/` — 深度分析产出作为互动内容输入
  - 只读：`scripts/daily/` — 分析管道（引入时标注 from scripts.daily.）
  - 零硬编码 import 依赖，路径配置在 `servers/textbook/config.py`
  - 总经办项目必须位于约定路径，否则 textbook server 无法启动
- `frontend/` 由 总经办 `scripts/dashboard/` 拆分独立而来
- 其他 servers 无此跨项目依赖

## 协作规则

- 用户不在时不自动执行
- 代码改动由 AI 写、用户 review
- 方向性决策需用户确认后才实施

## 继承的全局约束（自动生效）

S01-S11（参数验证、失败告警、跨项目对比、Windows编码防御、修改验证等）
六原则（闭环验证 / 最少工具 / 关键前置 / 可恢复 / 全程可视 / 度量驱动）
控制论卡（反馈闭环 / 稳定性 / 捉主要矛盾 / 实践闭环 / 内因优先 / 护栏）
