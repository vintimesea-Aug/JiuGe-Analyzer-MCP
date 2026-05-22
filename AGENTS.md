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
│   └── research/
├── core/                 ← 共享基础设施
├── tests/
└── data/                 ← 缓存
```

## MCP 开发规则

- 每台 server 独立可部署、可卸载
- 优先用 Python MCP SDK
- LLM 调用优先走 env var 中的 API key，fallback 到 Ollama
- core/ 中的基础设施不做泛化抽象，只做当前够用

## 协作规则

- 用户不在时不自动执行
- 代码改动由 AI 写、用户 review
- 方向性决策需用户确认后才实施

## 继承的全局约束（自动生效）

S01-S11（参数验证、失败告警、跨项目对比、Windows编码防御、修改验证等）
六原则（闭环验证 / 最少工具 / 关键前置 / 可恢复 / 全程可视 / 度量驱动）
控制论卡（反馈闭环 / 稳定性 / 捉主要矛盾 / 实践闭环 / 内因优先 / 护栏）
