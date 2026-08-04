# 意图识别Agent - 完整项目方案

## 📋 项目概述

一个专业的**客服对话意图识别系统**，支持对客服会话进行7维度的结构化分析和标注。

- ✅ **7维度标注框架**：语义压缩、商家情绪、用户诉求、达成一致、方案、介入时机、介入类型
- ✅ **大模型驱动**：集成公司Agent平台，支持多种大模型
- ✅ **批量处理**：支持同时处理多条对话，并发能力强
- ✅ **多格式支持**：输入/输出支持JSON/CSV/Excel/JSONL
- ✅ **生产就绪**：包含工作流、错误处理、进度追踪等完整功能

---

## 🚀 快速开始

### 基础使用

```python
from workflow.orchestrator import IntentRecognitionWorkflow
from company_platform import get_llm_service

# 初始化工作流
llm_service = get_llm_service()  # 从公司平台获取LLM服务
workflow = IntentRecognitionWorkflow(llm_service)

# 执行工作流
result = workflow.execute(
    input_source="input/dialogs.csv",
    input_format='csv',
    output_format='excel',
    model_name='gpt-4',
    parallel=True
)

# 查看结果
print(result['summary'])
print(f"输出文件: {result['output_path']}")
```

---

## 📊 7维度标注框架

| 维度 | 类型 | 说明 |
|------|------|------|
| 1️⃣ **语义压缩** | 必填 | 提炼核心矛盾/事件，用`**加粗**`标注关键点 |
| 2️⃣ **商家情绪** | 必填 | 评估客服服务表现：正向/中性/负向/强烈负向 |
| 3️⃣ **用户诉求** | 可选 | 用户明确的诉求类型（8类） |
| 4️⃣ **是否达成一致** | 必填 | 是/否/无法判断 |
| 5️⃣ **达成一致方案** | 条件 | 仅当维度4=是时标记（9类方案） |
| 6️⃣ **介入时机** | 必填 | 是/否（检查4个触发条件） |
| 7️⃣ **介入时机类型** | 条件 | 仅当维度6=是时标记（4类类型） |

---

## 🤖 大模型集成

### 触发大模型能力

在公司Agent平台上，大模型调用点位于 `skill/intent_analyzer.py`：

```python
# ⭐【大模型触发点】
response = self.llm_service.call(
    system_prompt=system_prompt,
    user_prompt=user_prompt,
    model_name=model_name or "default",  # 平台自动调度
    temperature=0.3,
    max_tokens=2000,
    response_format="json"
)
```

**特点**：
- ✅ 无需API KEY（公司平台认证）
- ✅ 支持多种大模型（GPT-4、Claude、本地模型等）
- ✅ 支持并发调用
- ✅ 自动重试和错误恢复

---

## 🔄 工作流说明

### 工作流的5个步骤

```
📥 加载输入 → 🤖 触发大模型分析 → ✅ 处理验证 → 💾 导出结果 → 📊 生成报告
```

---

## 📋 项目结构

```
my-skill-rope/
├── README.md
├── config/
│   ├── prompt_template.py          # 系统提示词模板
│   └── dimensions_config.py        # 维度定义与配置
├── skill/
│   └── intent_analyzer.py          # 核心分析Skill（大模型触发点）
├── workflow/
│   ├── orchestrator.py             # 工作流编排器
│   └── batch_processor.py          # 批量处理器
├── utils/
│   └── format_converter.py         # 多格式转换工具
└── knowledge_base/
    └── dimensions_definition.json  # 知识库
```

---

## ⚙️ 在公司Agent平台上的部署

### 1. Skill注册

```python
SKILL_METADATA = {
    "skill_name": "intent_recognition",
    "skill_type": "analysis",
    "llm_required": True,  # ⭐ 标识需要触发大模型
    "supported_models": ["gpt-4", "claude-3", "local_model"],
    "parallelism": True
}
```

### 2. 工作流配置

在平台的工作流编辑器中配置，支持：
- 手动触发
- 定时触发
- API触发
- 事件触发

---

## 📈 支持的输入/输出格式

**输入格式**：JSON、CSV、Excel、JSONL（自动识别）

**输出格式**：JSON、CSV、Excel、JSONL（可选择）

---

## 🎯 项目特性总结

✨ **核心优势**：
- 🚀 大模型驱动，精准度高
- 📊 结构化输出，易于集成
- ⚡ 并发处理，性能卓越
- 🔄 多格式支持，兼容性强
- 🛡️ 完整的错误处理和恢复机制
- 📈 自动生成分析报告
- 🔧 高度可配置，易于定制

---

**版本**: 1.0.0