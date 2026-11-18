# 使用指南

## 环境与边界

本仓库由给 AI 助手执行的工作流说明和三个辅助命令组成。Python 脚本负责初始化、文件扫描和校验；全文阅读、语义判断、Excel 写入与视觉检查由具备相应工具的助手完成。

- Python 3.10 或以上；`openpyxl` 3.1.2 或以上，用于富文本校验。
- 内容抽取先尝试 MarkItDown；PDF 抽取可在需要时安装 `python -m pip install "markitdown[pdf]"`。其安装要求以 [MarkItDown 官方说明](https://github.com/microsoft/markitdown) 为准；它不属于三个辅助命令的必要依赖。
- 助手还需要本地文件访问、PDF 阅读和保留富文本的 Excel 写入能力；视觉检查需额外的渲染工具。不要假定只有本仓库就具备这些能力。
- 当前正式综述面向英文论文，九个正文列默认英文，知识卡片中文。`--final` 检查 inventory 的 `Language` 是否为 `English`。这不是已验证的全学科、全语言通用方案。

## 初始化与扫描

在仓库根目录执行：

```bash
python -m pip install -r requirements.txt
python scripts/init_workspace.py ./my-review
```

将有权使用的全文 PDF 放入 `my-review/papers/` 后运行：

```bash
python scripts/scan_papers.py ./my-review
```

扫描命令只登记本地 PDF 路径并从文件名生成待核对标题，不下载论文，不核验元数据，也不证明文件是完整、可读的全文。已有 metadata 会尽量按 PDF 路径保留；请避免同时编辑 inventory，并先备份重要文件。

## 让助手执行工作流

```text
请读取本仓库 SKILL.md，按其中的 references 规范处理 ./my-review。
先核对本地全文与 source_inventory.csv，只完成一篇论文作为原型。
生成固定 16 列、每篇一行的 Excel，并同步中文知识卡片。
九个正文字段逐一回到原文核验，保留页码、章节、图表或公式定位。
先尝试 MarkItDown 抽取，必要时用 PDF 工具补充。
请完成格式校验和视觉检查，并把需要我核对的问题单独列出。
```

现有工作簿应先只读审计，保存版本化副本，单篇原型经用户确认后再处理其余论文。主表没有附加 PDF 列；论文行与本地文件的映射需要通过书目信息、inventory 和知识卡片人工核对。

## 校验与交付

只有在助手已生成工作簿后才执行：

```bash
python scripts/validate_workspace.py ./my-review --workbook ./my-review/文献综述.xlsx --json-report ./my-review/outputs/validation.json
```

正式交付检查：

```bash
python scripts/validate_workspace.py ./my-review --workbook ./my-review/文献综述.xlsx --json-report ./my-review/outputs/validation-final.json --final
```

工作区是**位置参数**，没有 `--root` 参数。含空格的路径用引号包围。错误会使命令返回非零退出码；警告仍需逐项判断，不应机械忽略。

自动校验覆盖表头、非空字段、部分富文本规则、来源行格式，以及 inventory 中部分文件存在性和元数据要求。**它不会打开 PDF 核验全文、逐句比对事实、证明页码正确、证明创新成立，也不会完整验证知识卡片与 Excel 的语义一致性。** 这些仍需执行工作流并人工复核。

`--final` 是增加结构门禁，不代表科学事实已通过认证。若项目有专门的 PDF gate，按工作流先执行该门禁。

## 工作区文件

```text
my-review/
├── papers/                    # 本地论文全文
├── source_inventory.csv       # 文件与书目信息清单
├── 文献综述.xlsx                # 由助手生成，初始化命令不会创建
├── 知识卡片.md                 # 初始化时创建模板，随后由助手填充
└── outputs/                   # 报告与版本化输出
```

`init_workspace.py` 创建目录、inventory 表头和知识卡片模板，不会生成完整 Excel。没有真实全文的论文留在候选或缺口清单。
