---
name: literature-review-workspace
description: Use when creating, revising, auditing, or continuing a literature-review workspace that combines local scholarly PDFs, a traceable Excel review table, source inventory, and Chinese knowledge cards; also use when the user asks to repair Problem/Object/Constraints/Model/Solution/Data/Scale/Results/Innovation content, classification, citations, or rich-text highlighting in a literature-review workbook.
---

# 文献综述工作区

## 目标

把论文原文、Excel 综述和知识卡片组织成可追溯闭环：

```text
本地 PDF -> 全文定位 -> 单行综述 -> 蓝色来源位置 -> 中文知识卡片
```

本 skill 的正式成果通常包括：

1. `papers/` 下的原始 PDF；
2. `source_inventory.csv`；
3. 16 列单行主表 `文献综述*.xlsx`；
4. `知识卡片.md`；
5. 校验报告。

只做单篇论文总结时，可执行全文阅读、字段写作和知识卡片阶段；只审查现有 Excel 时，可执行基线审计和校验阶段。

## 强制优先级

按以下顺序处理冲突：

1. 用户本轮明确要求；
2. 离目标文件最近的 `AGENTS.md`；
3. 用户指定的参考工作簿；
4. 本 skill 当前规则；
5. 历史工作区习惯。

参考工作簿用于学习内容边界、密度和视觉效果，不覆盖用户后来明确修正的规则。

## 正式论文门禁

论文进入正式 Excel 或 canonical `知识卡片.md` 前必须满足：

- 本地存在可打开的全文 PDF；
- PDF 位于工作区 `papers/`；
- `source_inventory.csv` 中的 `PDF filename` 与真实文件一致；
- 字段结论来自全文，不用摘要、DOI 或元数据冒充全文阅读；
- 每个正文单元格末尾有可核查的页码、章节、图、表或公式定位。

没有本地 PDF 的论文只能进入候选或缺口清单，不得为了凑数量写入正式综述。

若项目提供 PDF gate 脚本，必须先运行并通过。门禁失败时，不得把文件命名为正式完成版。

## 内容抽取顺序

当任务涉及 PDF、Word、PPT、Excel、HTML 或图片中的内容抽取、总结或结构化时：

1. 先尝试 MarkItDown；
2. 若表格、公式、页码或版式丢失，再用相应的 PDF/Office 解析工具；
3. 需要保留 Excel 富文本和版式时，用能保留 rich text 的工作簿工具；
4. 最终来源位置必须回到原始 PDF 核验。

## Excel 唯一正式结构

每篇论文一行，固定 16 列，顺序和名称必须完全一致：

```text
日期 | 类别 | 关键词 | authors | journal | Year | Title |
Problem | Object | Constraints | Model | Solution | Data | Scale |
Results | Innovation
```

不要恢复历史 `Summary / Evidence / Source` 三行结构；不要插入截图、Excel 注释、DOI 列、PDF File 列或其他辅助列，除非用户明确要求。

### 书目信息

- `日期`：录入或复核日期，沿用工作簿现有格式。
- `类别`：按论文实际核心问题分类。允许四大主题之外的新类别；不得把空箱调运、泊位分配、航线网络等硬塞进“港口规划、动态定价、鲁棒优化、绿色港口”。
- `关键词`：保留检索价值最高的术语，只加粗 1–2 个最核心关键词。
- `authors / journal / Year / Title`：忠实记录论文元数据，不做内容型高亮。

### 九个正文字段

写作前必须完整阅读 [J/M 范本字段写作规范](references/jm-template-writing-spec.md)。最重要的边界如下：

- `Problem`：现实或学术问题、缺口、决策冲突及其重要性。
- `Object`：被研究、预测、调度或优化的对象；不是目标函数或优化目标。
- `Constraints`：运营限制、关键假设、不确定性、可行域和模型/数据困难；不是案例规模。
- `Model`：模型名称、结构、模块、变量关系、耦合方式或算法架构；不是公式清单，也不逐条解释某公式做什么。
- `Solution`：作者怎样求解或应用模型，按工作流写主要步骤。
- `Data`：具体数据来源、数据类型、输入变量及场景生成方法。
- `Scale`：数量、规模、范围、时长和实例配置；即使出现在 case study，也要逐项判断后放入 Scale。
- `Results`：有比较基准、方向和数值证据的主要发现及管理含义。
- `Innovation`：相对既有研究真正新增的理论、模型、数据、算法或应用贡献。

### 写作顺序与重点

九个字段不得按摘要顺序机械搬运。先确定本列要回答的问题，再按以下顺序组织内容：

- `Problem`：研究问题或决策冲突先行，再说明现有研究缺口及其后果；不要先铺陈宽泛背景。
- `Model`：压缩为模型框架及其作用，优先用一句紧凑表述交代核心结构、耦合关系或模块分工；不堆公式。
- `Solution`：区分求解方法与实验分析。先写解析推导、优化、训练或算法流程，再写数值实验、仿真、案例或敏感性分析。
- `Data`：只写数据来源、数据类型、输入变量及场景生成方式；不写样本数量、时空范围、结果或结论。
- `Scale`：集中写研究对象数量、样本或记录数、时间与空间范围、情景数、参数范围、重复次数和实例配置；不写数据来源。
- `Results`：核心结论或主要机制先行，再补比较基准、影响方向和关键数值。
- `Innovation`：依据全文实际贡献点确定数量，一个创新点对应一个独立表述；有几个写几个，只有一个就只写一个，不得固定凑成两点或三点。

以上顺序不改变下文的 Data/Scale 边界、缩写全称和富文本规则。原文没有相应事实时不得为了满足句式而补写或推断。

### Data 与 Scale 判定

逐项问：

- 它回答“数据从哪里来、是什么、包含哪些变量、如何生成”吗？是则放 `Data`。
- 它回答“有多少、多大、多长、覆盖什么范围、如何配置实例”吗？是则放 `Scale`。

不要把整个 case study 原封不动放进 Data，也不要把数据来源放进 Scale。一个句子同时包含两类信息时，拆开改写。

## 写作质量规则

- 用英文清楚、准确地概括原文，不复制摘要，不堆砌公式。
- 每个字段只回答本列问题，避免同一句在多个字段重复。
- 保留足够上下文，使加粗或描红片段本身语义完整。
- 不夸大作者未声称的创新、因果关系或普适性。
- 优先保留定量结果、比较基准、适用边界和实例配置。
- 新增选文默认优先 2024 年及以后；较早论文只在奠基性、不可替代或高度相关时保留。

### 缩写必须给出全称

- `类别`、`关键词` 和 `Problem–Innovation` 中出现的每个专业缩写，必须在该单元格第一次出现时写为 `Full Name (ABBR)`。
- 每个单元格必须能独立阅读；不能因为 `Model` 已解释某缩写，就在 `Solution`、`Data`、`Scale` 或其他列直接裸写该缩写。
- 同一单元格完成第一次定义后，后文可以只使用缩写。
- 多个缩写必须分别定义，禁止写成未展开的组合串，如 `MFD-LRHO-DSO/DRC-MLN`。
- 中文类别优先直接写中文全称，例如写“传统人工智能”，不要只写 `AI`。
- 论文官方 `Title`、作者、期刊名和年份保持原文，不因本规则改写。
- 来源定位使用完整的 `page / pages / Section / Figure / Table / Equation`，不要写 `p. / pp. / Sec. / Fig. / Eq.`。

示例：`Macroscopic Fundamental Diagram (MFD)`、`Linear Rolling Horizon Optimization (LRHO)`、`Dynamic System Optimum (DSO)`、`Multi-Layer Neural Network (MLN)`。

推荐正文词数（不含蓝色来源行）：

| 字段 | 英文词数 |
|---|---:|
| Problem | 55–90 |
| Object | 8–25 |
| Constraints | 20–45 |
| Model | 10–30 |
| Solution | 40–70 |
| Data | 20–45 |
| Scale | 15–50 |
| Results | 35–65 |
| Innovation | 25–80，总计；每个创新点约 15–30 |

词数是密度提示，不是机械截断线。准确性和字段边界优先。

## 富文本语义

### 黑色加粗

`Problem–Results` 每个非空单元格至少有一处黑色加粗重点。重点可以是完整句，也可以是语义完整的分句；不强制整句，但禁止只加粗孤立术语、单个数字或过短片段。一个单元格可以有多处加粗。

九个正文字段必须全部兼顾，不能只高亮 Problem、Model 或 Results。

### 红色加粗

红色仅用于 `Innovation` 中真实的创新点。每个独立创新点分别把相符的完整句或语义完整分句设为红色加粗；有几个创新点就标几处。背景、问题说明和过渡语保持黑色常规字。

### 蓝色来源行

`Problem–Innovation` 每个单元格末尾另起一行，使用蓝色、非加粗、非红色的括号来源位置，例如：

```text
(page 4, Section 2.1; page 11, Table 3)
```

来源行必须来自全文页码、章节、图、表或公式定位。正文重点与来源行不得混色。

### 禁止项

- `类别` 不加粗、不描红；
- 红色不得出现在 `Innovation` 之外；
- `Innovation` 不能整格全红，除非整格确实只包含一个创新陈述和蓝色来源行；
- 来源行不能加粗或描红；
- 不用截图、批注或隐藏列代替正文来源定位。

## 七阶段工作流

完整流程见 [阶段工作流](references/stage-workflow.md)。主流程为：

1. 初始化与规则识别；
2. 候选检索和年份/主题筛选；
3. PDF 入库和 inventory 门禁；
4. 全文抽取与来源定位；
5. 字段写作和知识卡片同步；
6. Excel 富文本与视觉检查；
7. 自动校验、人工抽查和交付。

## 修改现有工作簿

返工时先做只读基线审计，再编辑：

1. 确认工作簿、工作表、表头和论文行数；
2. 将每一行可靠映射到本地 PDF；
3. 记录缺失字段、字段错位、错误分类、Data/Scale 混淆、富文本缺口和来源缺口；
4. 不信任旧单元格内容；回到全文逐字段重建；
5. 保留用户未要求改变的工作表结构、列宽、行高、冻结窗格和基本样式；
6. 先制作 1 篇原型并进行视觉核验；
7. 用户确认原型后，才批量处理其余论文。

不要覆盖唯一原件。先保存版本化副本；确认后再按用户要求替换 canonical 文件。

## 工具与脚本

### 初始化

```powershell
python scripts/init_workspace.py <workspace>
```

### 扫描 PDF

```powershell
python scripts/scan_papers.py <workspace>
```

### 校验

```powershell
python scripts/validate_workspace.py <workspace> --workbook <xlsx> --json-report <report.json>
```

正式交付时加 `--final`。校验器检查：

- 16 列表头和单篇单行结构；
- PDF/inventory/card 门禁；
- 正文字段非空和来源行；
- `Problem–Results` 黑色语义完整重点；
- `Innovation` 红色加粗创新点；
- 红色越界、来源行混色、类别误高亮；
- 图片、批注和推荐词数。

校验器只能发现结构和格式问题，不能替代全文事实核验。最终仍需人工抽查分类、字段边界、Data/Scale 和创新真实性。

## 原子化验证点

长任务按可观察结果拆分：

- PDF gate 通过；
- 单篇内容卡完成；
- 单篇 Excel 原型完成并渲染检查；
- 小批量校验通过；
- 全量校验和抽查通过。

当同一类操作重复三次以上，应优先复用脚本或校验器，但不得自动化删除、权限修改或生产替换。

## 完成标准

只有同时满足以下条件，才能称为正式完成：

- 正式论文均有本地 PDF，inventory 无缺口；
- Excel 恰为 16 列、每篇一行；
- 分类不生搬硬套；
- 九个字段语义准确，Data/Scale 和 Object/Model 边界正确；
- 每个单元格中的专业缩写首次出现均有全称，来源定位不使用缩写标签；
- 所有正文字段都有合格重点和蓝色来源行；
- Innovation 按创新点红色加粗，其他列无红色；
- 知识卡片与 Excel、PDF 一致；
- 自动校验无错误，警告已逐项确认；
- 已完成至少一轮视觉检查和人工抽查。
