# J/M 范本文献综述写作规范

本文件是 16 列文献综述工作簿的唯一详细写作契约。处理、返工或验收综述 Excel 时必须阅读它。

## 范本用法

- M 范本决定英文内容的粒度、九列分工和整体密度。
- J 范本的有效增量是“类别”列；其前 14 篇的 `Problem–Innovation` 与 M 相同，不当作独立双倍样本。
- 范本中的 Data/Scale 混写、夸张形容词、无来源行和颜色漂移不得复制。
- 建议字数是写作校准线，不是凑字数目标；不包括末尾蓝色来源行。

## 固定表头

```text
日期 / 类别 / 关键词 / authors / journal / Year / Title /
Problem / Object / Constraints / Model / Solution / Data / Scale / Results / Innovation
```

- 每篇论文只占一行。
- 不增加 DOI、PDF File、Evidence、Screenshot、Limitations、Review Use 或备注列。
- 不使用 `Summary / Evidence / Source` 三行结构，不嵌入截图，不添加 Excel 注释。

## 书目与索引列

| 列 | 写什么 | 格式 |
|---|---|---|
| 日期 | 整理日期或用户指定日期，不是发表年。 | 沿用工作簿现有日期格式。 |
| 类别 | 论文真实研究主题，可组合 1–2 个中文标签。 | 不加粗、不描红。 |
| 关键词 | 原文关键词或与研究高度相关的检索词。 | 分号分隔；最相关的 1–2 个可黑色加粗。 |
| authors | 作者原始顺序。 | 多人用分号分隔。 |
| journal | 标准期刊或会议全名。 | 不写 DOI、链接或分区。 |
| Year | 发表年。 | 只写四位数字。 |
| Title | 原文题名。 | 保留原文大小写和副标题。 |

分类不是“港口规划 / 动态定价 / 鲁棒优化 / 绿色港口”四选一。只有核心问题确实属于该主题时才使用对应标签；否则使用舱位分配、空箱调运、泊位调度、航运运营、码头作业、船舶时间预测等真实主题。

## 九个综述字段

| 字段 | 代表什么 | 应写内容 | 原文优先位置 | 建议单词数 |
|---|---|---|---|---:|
| Problem | 为什么要研究 | 现实痛点、现有方法不足、研究空白及造成的后果。建立“问题—缺口—影响—需求”逻辑，不写解决步骤。 | Abstract, Introduction, research gap, problem statement | 55–90 |
| Object | 研究、预测或优化的对象 | 例如 vessel arrival time、container dwell time、berth plan、slot allocation、price or demand。`Object` 不是 `Objective`；不写“最小化成本”等目标函数，除非该目标本身就是被研究对象。 | Title, Abstract, problem definition, model scope | 8–25 |
| Constraints | 什么限制了问题或模型 | 运营限制、关键假设、数据不完整/不平衡、不确定性、边界和可行性条件。不写数据来源、样本数或 case 规模。 | Assumptions, formulation, constraints, limitations | 20–45 |
| Model | 作者用什么模型表示问题 | 模型名称、架构、组成模块、决策变量及关系、耦合机制或算法架构。不罗列公式，不逐条解释“某个公式做什么”。 | Model, method, formulation, framework, algorithm | 10–30 |
| Solution | 作者具体怎样解决 | 数据处理、模型构建、求解/训练、更新、仿真和应用流程。说清步骤和衔接，不重复 Model 中的名称清单。 | Proposed approach, procedure, solution algorithm | 40–70 |
| Data | 使用了什么具体数据 | 数据集/数据库、采集或记录来源、数据类型、输入变量、真实/仿真属性和场景生成方式。不用笼统的“case study”代替数据。 | Data, case study, experiment, simulation setup | 20–45 |
| Scale | 数据、case 或实验有多大 | 样本/记录/船舶/集装箱数，港口/码头/路线/节点/设备数，时间跨度，空间范围，情景数，训练测试划分，参数范围、重复次数和实例配置。内容即使出现在 case study 小节，只要回答“多少/多大/多久/怎样配置”就归入 Scale。 | Experiment settings, case parameters, instance configuration | 15–50 |
| Results | 研究实际得到了什么 | 核心数值、基准对比、改进幅度、显著影响因素、稳健性/敏感性及实际意义。不只写“effectively”或“performs better”。 | Results, numerical experiments, tables, conclusion | 35–65 |
| Innovation | 相对已有研究真正新在哪里 | 以已有研究为参照，分别写出新对象、新机制、新数据、新集成或新应用中的真实贡献。方法名称、普通结果和“效果更好”不自动构成创新。 | Contributions, introduction ending, conclusion | 每点 15–30，总计 25–80 |

## 写作顺序与重点

不要把摘要换词后按顺序分散到九列。每列先回答自己的问题，再组织证据：

| 字段 | 推荐组织顺序 |
|---|---|
| Problem | 研究问题或决策冲突 → 现有研究缺口 → 缺口造成的后果或本研究必要性。 |
| Model | 核心模型框架 → 主要模块、层级或耦合关系 → 框架用于表示什么问题。尽量压缩为一句，不罗列公式。 |
| Solution | 解析推导、优化、训练或算法求解 → 数值实验、仿真、案例验证或敏感性分析。两部分需要明确区分。 |
| Data | 数据来源 → 真实、仿真或生成属性 → 数据类型、输入变量和场景生成方式。 |
| Scale | 对象或样本数量 → 时间与空间范围 → 情景数、参数范围、重复次数和实例配置。 |
| Results | 核心结论或主要机制 → 相对基准与影响方向 → 最能支撑结论的关键数值。 |
| Innovation | 逐项回查原文 contributions、research gap 和 conclusion，按实际创新点数量分别表述；不固定凑点。 |

`Data` 不承担规模信息，`Scale` 不承担数据来源信息。创新点只有一个时只写一个；存在多个独立创新点时分别写出，并分别设置红色加粗。

## Data 与 Scale 逐项判断

对每条 case-study 信息问两个问题：

1. 它在回答“用了什么数据/输入”吗？是则进 `Data`。
2. 它在回答“数据、时空范围或实验配置有多大”吗？是则进 `Scale`。

例如：

- `Automatic Identification System position, course and speed records` -> Data。
- `2,722 vessels at one Busan terminal during 2022` -> Scale。
- `Demand scenarios generated from a fitted distribution` -> Data；具体情景数和参数范围 -> Scale。

不因原文小节名为 `Case study` 就将整段写进 Data。

## 缩写与全称

- `类别`、`关键词` 与九个正文字段分别独立检查。
- 每个单元格第一次出现专业缩写时，必须写为 `Full Name (ABBR)`；完成定义后，该单元格内才可单独使用缩写。
- 不能跨单元格继承定义。例如 `Model` 已写 `Dynamic System Optimum (DSO)`，`Solution` 首次出现时仍需重新写全称。
- 多个缩写必须逐个展开，不写裸露的缩写组合串。
- 标准来源标签也写全：`page / pages / Section / Figure / Table / Equation`。
- 官方题名、作者和期刊元数据保持原貌。

缩写全称会增加词数；当完整定义使字段略超推荐范围时，优先保证可独立理解，再压缩重复解释。

## 高亮的语义

### 黑色加粗

- `Problem–Results` 每个非空单元格至少有一处黑色加粗的重点信息。
- 加粗可以是完整句，也可以是语义完整的关键分句；不强制句号边界。
- 不得只加粗一个方法名、孤立变量或几个不能独立传达信息的词。
- 字段内有多个核心信息时可加粗多处，不设数量上限。
- `Object / Model / Data / Scale` 较短时，可加粗整个语义单元。

### 红色加粗

- 红色只表示 `Innovation` 中的真实创新点。
- 有几个创新点，就将几个对应的完整信息片段设为红色加粗；不强制每点为完整句。
- Innovation 中的背景、解释和来源行保持黑色或蓝色普通字。
- 非 Innovation 字段不使用红色，避免颜色语义漂移。

### 蓝色来源行

每个 `Problem–Innovation` 单元格末尾都使用：

```text
正文内容。
(page 4, Section 3, Equations (1a)-(1e); page 11, Table 2)
```

- 来源位置必须换行，整体保留括号。
- 来源文字必须蓝色、不加粗、不描红。
- 位置来自本地 PDF 全文页码、章节、图、表、公式或算法；不用 DOI、摘要页链接或文件名伪装全文定位。
- 一个字段需要多处支撑时，在同一括号中用分号分隔。

## 准确性检查

- 九列必须分别回到 PDF 查找，不将一段总摘要拆成九列。
- 将原文转述为简洁、可独立理解的英文，不长段复制。
- 原文没有说明时，写 `Not clearly specified in the paper.` 并标出已核查位置，不猜测。
- 删除 `fundamentally`、`completely`、`absolute superiority`、`brilliantly` 等无证据的宣传性词。
- 结果数值必须核对指标名、单位、对比对象和改进方向；对 Root Mean Square Error (RMSE)、Mean Absolute Error (MAE) 等指标进行内部一致性检查。

## 最终验收

- 16 列顺序精确，每篇只一行。
- 内嵌图片和 Excel 注释均为 0。
- 九个综述字段非空，蓝色来源行齐全。
- `Problem–Results` 每格都有语义完整的黑色加粗重点。
- `Innovation` 每个真实创新点有对应红色加粗信息片段。
- 分类忠实反映论文主题，Data/Scale 逐项分清，Model/Solution 不重复。
- 自动校验只能保证结构和样式；分类、高亮重点和创新点的语义准确性仍必须依据 PDF 人工审核。
