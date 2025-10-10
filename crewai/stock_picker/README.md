# 🎓 **CrewAI 实战笔记: 构建 "Stock Picker" 智能代理**

这是一份关于使用 CrewAI 框架构建一个自动化股票挑选项目的深度学习笔记。项目旨在探索 CrewAI 的多项核心功能，并构建一个从新闻趋势发现、财务研究到最终决策的完整工作流。

## 🎯 **1. 项目目标与核心功能探索**

本次项目不仅是完成一个任务，更是一次对 CrewAI 框架高级特性的深度探索。我们将重点关注以下三大功能：

* **📦 结构化输出 (Structured Outputs)**: 利用 Pydantic 模型强制任务输出为规范的 JSON 格式，确保数据流的稳定与可靠。
* **🔧 自定义工具 (Custom Tools)**: 超越框架内置工具，亲手打造一个用于发送推送通知的本地工具，扩展 Agent 的能力边界。
* **📊 层级化流程 (Hierarchical Process)**: 引入一位 `Manager` Agent 来动态分配和协调任务，实现更灵活、更自主的 AI 工作流，而非固定的顺序执行。

## ⚙️ **2. 项目初始化与配置**

一个稳固的基础是项目成功的关键。本节记录了从项目创建到定义 Agents 和 Tasks 的全过程。

### **2.1. 项目脚手架**

通过 `crewai-cli` 快速生成项目结构。

1. **进入工作目录**: `cd your/project/path`
2. **执行创建命令**:
   ```bash
   crewai create stock_picker
   ```
3. **向导配置**:
   * LLM Provider: `Deepseek,Dashscope`
   * Model: `deepseek-chat,qwen-plus`

### **2.2. 👥 Agents 定义 (`src/config/agents.yaml`)**

Agents 是我们工作流中的核心执行者。我们定义了四个角色鲜明的 Agent：

| Agent 名称                        | 角色 (Role)    | 目标 (Goal)                                        | 背景故事 (Backstory)                                 |
| :-------------------------------- | :------------- | :------------------------------------------------- | :--------------------------------------------------- |
| **Trending Company Finder** | 趋势公司发现者 | 在特定领域新闻中识别2-3家热门公司以供分析。        | 一位新闻阅读专家，善于从信息洪流中发现趋势。         |
| **Financial Researcher**    | 财务研究员     | 对给定的公司提供全面的财务分析报告。               | 一位在深入分析热门公司方面有卓越记录的金融专家。     |
| **Stock Picker**            | 股票挑选者     | 从研究报告中挑选最佳投资对象，并通知用户。         | 一位细致、技术娴熟的金融分析师，拥有可靠的选股业绩。 |
| **Manager**                 | 经理           | 作为项目经理，将任务分配给其他 Agents 以达成目标。 | 目标是高效、自主地协调团队，挑选出最佳投资公司。     |

### **2.3. 📝 Tasks 定义 (`src/config/tasks.yaml`)**

Tasks 是 Agents 需要完成的具体工作。我们定义了三个环环相扣的核心任务：

| 任务名称                              | 描述                                             | 分配的 Agent                | 上下文依赖 (Context)                 |
| :------------------------------------ | :----------------------------------------------- | :-------------------------- | :----------------------------------- |
| **Find Trending Companies**     | 搜索最新新闻，找到所在领域的新兴热门公司。       | `Trending Company Finder` | 无                                   |
| **Research Trending Companies** | 对给定的公司列表进行详细分析，并生成报告。       | `Financial Researcher`    | `Find Trending Companies` 任务     |
| **Pick Best Company**           | 分析研究结果，挑选最佳公司，并通过推送通知用户。 | `Stock Picker`            | `Research Trending Companies` 任务 |

> 💡 **Pro-Tip: 提示工程 (Prompt Engineering)**
> 在定义 Agents 和 Tasks 时，保持术语的一致性至关重要。例如，在多个地方统一使用 “trending companies” 可以显著提高模型响应的连贯性和稳定性。

## 💻 **3. 核心实现 (`crew.py`)**

`crew.py` 是将配置文件中的静态定义转化为动态可执行代码的核心。

### **3.1. 强制输出格式: Pydantic 模型**

为确保数据在任务间可靠传递，我们为关键任务定义了 Pydantic 输出模型。

1. **定义单个实体模型**: 创建一个 `BaseModel` 类，包含名称、股票代码等字段。
2. **定义列表模型**: 再创建一个 `BaseModel`，其字段为第一步模型的列表 `List[Model]`。
3. **在 Task 中应用**: 在 `Task` 实例化时，通过 `output_pydantic` 参数指定模型。

**本项目使用的 Pydantic 模型：**

| 模型名称                        | 用途                                             |
| :------------------------------ | :----------------------------------------------- |
| `TrendingCompany`             | 封装单个热门公司的基本信息（名称、代码、原因）。 |
| `TrendingCompanyList`         | 组织 `TrendingCompany` 对象的列表。            |
| `TrendingCompanyResearch`     | 结构化存储对一家公司的详细研究报告。             |
| `TrendingCompanyResearchList` | 组织多个公司研究报告对象的列表。                 |

### **3.2. 集成自定义工具: `PushNotificationTool`**

为了让 Agent 能与外部世界交互，我们构建了一个自定义工具。

1. **定义输入模式**: 创建 `PushNotificationInput(BaseModel)`，定义工具需要的参数（如 `message: str`）。
2. **构建工具类**: 创建 `PushNotificationTool`，设置 `name`、`description` 和 `args_schema`。
3. **实现核心逻辑**: 在 `_run` 方法中编写发送通知的实际代码。
4. **赋能 Agent**: 在 `crew.py` 中，将 `PushNotificationTool()` 实例添加到 `Stock Picker` Agent 的 `tools` 列表中。

**`PushNotificationTool` 详解:**

| 属性/方法              | 配置                      | 作用                                         |
| :--------------------- | :------------------------ | :------------------------------------------- |
| `args_schema`        | `PushNotificationInput` | 定义了工具必须遵循的参数模式。               |
| `_run(message: str)` | Method                    | 包含了调用 Pushover 服务发送通知的业务逻辑。 |

### **3.3. 启用自主流程: 配置层级化 Process**

这是实现 `Manager` Agent 领导模式的关键步骤。

1. **独立实例化 Manager**: `Manager` Agent 不属于 `agents` 列表，需单独创建。
2. **开启授权**: 创建 `Manager` 实例时，设置 `allow_delegation=True`，允许它将任务分派给其他 Agent。
3. **配置 Crew**: 创建 `Crew` 实例时，进行如下设置：
   * `process`: `Process.hierarchical`
   * `manager_agent`: 指定第一步创建的 `Manager` Agent 实例。
   * `agents`: 传入**不包含** Manager 的 "worker" Agents 列表。

> 💡 **Manager 配置技巧**
> 为 `Manager` Agent 使用一个更强大的模型（如 GPT-4）通常能获得更好的任务分解和管理能力，尽管成本会更高。

## 🧠 **4. 高级主题: CrewAI 的记忆机制**

记忆功能让 Agent 能够从过去的交互中学习，避免重复工作。

* **短期记忆 (Short-Term Memory)**: 基于 RAG，存储在向量数据库中，用于任务执行时检索最近的相关信息。
* **长期记忆 (Long-Term Memory)**: 存储在 SQL 数据库中，用于积累长期知识。
* **实体记忆 (Entity Memory)**: 专门存储关于人物、地点等“实体”的信息。

**本项目中的 Agent 记忆配置:**

| Agent 名称                        | 是否启用记忆 (`memory=True`) | 原因                                                   |
| :-------------------------------- | :----------------------------- | :----------------------------------------------------- |
| **Trending Company Finder** | ✅ 是                          | 避免重复推荐已经发现过的公司，需要记住历史交互。       |
| **Financial Researcher**    | ❌ 否                          | 希望它每次都能执行全新的研究，而不是依赖旧的缓存信息。 |
| **Stock Picker**            | ✅ 是                          | 避免重复推荐同一支股票，需要记住之前已经推荐过的内容。 |

## ▶️ **5. 执行与总结**

### **5.1. 运行观察**

* **启动命令**: `crewai run`
* **流程的不可预测性**: 与顺序流程不同，层级化流程的执行路径是动态的。`Manager` Agent 可能会多次调用某个 Agent，这增加了灵活性但也降低了可控性。
* **成功验证**: 项目成功推荐了投资选择，并在 `outputs` 文件夹中生成了符合 Pydantic 模型的 JSON 文件，验证了结构化输出的成功。

### **5.2. CrewAI 项目构建流程总结**

1. **创建项目**: 使用 `crewai create <project_name>` 初始化项目结构。
2. **定义 Agents & Tasks**: 在 `.yaml` 文件中清晰地配置角色和任务。
3. **实例化 Crew**: 在 `crew.py` 中，通过装饰器和代码将配置实例化，并在此处配置**结构化输出**、**集成工具**和**流程模式**。
4. **更新 `main.py`**: 设置必要的输入参数。
5. **运行项目**: 使用 `crewai run` 启动。

---
