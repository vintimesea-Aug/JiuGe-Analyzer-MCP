"""Interactive content generator — reads deep_dives MD + LLM → interactive modules.

Supports: simulator, quiz, comparison module types.
Output is consumed by luffa_bridge.py for Luffa SuperBox packaging.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.llm import call_llm_json, default_model
from servers.textbook.config import DEEP_DIVES_DIR, LLM_MODEL, LLM_MAX_TOKENS


def list_topics() -> list[str]:
    """List available deep_dive topics (MD files in deep_dives dir)."""
    if not os.path.isdir(DEEP_DIVES_DIR):
        return []
    return sorted(
        f.replace(".md", "")
        for f in os.listdir(DEEP_DIVES_DIR)
        if f.endswith(".md")
    )


def read_deep_dive(topic: str) -> str:
    """Read a deep_dive MD file by topic name (with or without .md suffix)."""
    filename = topic if topic.endswith(".md") else f"{topic}.md"
    filepath = os.path.join(DEEP_DIVES_DIR, filename)
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Deep dive not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


SYSTEM_PROMPT = """你是一个互动教材内容生成器。从输入的深度分析文章中提取关键概念，生成互动学习模块。

输出必须是一个 JSON 对象，格式如下：
{
  "topicId": "主题标识",
  "topicTitle": "主题标题",
  "topicDescription": "一句话描述",
  "modules": [
    { "type": "simulator", ... },
    { "type": "quiz", ... },
    { "type": "comparison", ... }
  ]
}

模块类型说明：

1. simulator（模拟器）- 让用户调节参数、观察输出变化：
{
  "type": "simulator",
  "id": "唯一标识",
  "title": "模拟器标题",
  "description": "说明文字",
  "parameters": [
    { "id": "参数id", "label": "中文标签", "type": "number|select|slider", "min": 0, "max": 100, "default": 50, "unit": "单位", "options": ["选项"] }
  ],
  "formula": "计算公式的文字描述（非代码）",
  "chartConfig": { "xLabel": "X轴标签", "yLabel": "Y轴标签" },
  "explanation": "教育性解释：调节这个参数时会看到什么变化，为什么"
}

2. quiz（问答）- 多项选择题，附带解释：
{
  "type": "quiz",
  "id": "唯一标识",
  "title": "问答标题",
  "questions": [
    { "id": "q1", "text": "问题文字", "options": ["A", "B", "C", "D"], "correct_index": 0, "explanation": "答案解释" }
  ]
}
注意：correct_index 是 0-based 索引。最少 3 题，最多 8 题。

3. comparison（对比）- 两个概念/方案/时期的并排比较：
{
  "type": "comparison",
  "id": "唯一标识",
  "title": "对比标题",
  "left": { "title": "左侧标题", "description": "描述" },
  "right": { "title": "右侧标题", "description": "描述" },
  "dimensions": [
    { "label": "维度名称", "left": "左侧值", "right": "右侧值" }
  ]
}

规则：
- 从文章中提取至少 2 种模块类型（共 2-5 个模块）
- 内容必须忠实于原文，不编造数据
- 所有文字使用中文（除非原文是其他语言的专业术语）
- 确保 JSON 有效，所有字段完整"""


def generate_interactive(topic: str, module_types: list[str] | None = None) -> dict:
    """Read a deep_dive and generate interactive learning modules.

    Args:
        topic: Topic name (filename without .md suffix)
        module_types: List of desired module types, e.g. ["simulator", "quiz"].
                      If None, generates all types.

    Returns:
        dict with keys: topicId, topicTitle, topicDescription, modules[]
    """
    content = read_deep_dive(topic)

    types_hint = ""
    if module_types:
        types_hint = f"\n\n本次只需生成以下模块类型：{', '.join(module_types)}。每种类型 1-2 个模块。"

    user_prompt = f"请将以下深度分析文章转化为互动学习模块：\n\n---\n{content}\n---{types_hint}"

    result = call_llm_json(
        SYSTEM_PROMPT,
        user_prompt,
        model=LLM_MODEL or default_model(),
        max_tokens=LLM_MAX_TOKENS,
        temperature=0.3,
    )

    if "modules" not in result:
        result["modules"] = []
    if "topicId" not in result:
        result["topicId"] = topic
    if "topicTitle" not in result:
        result["topicTitle"] = topic

    return result
