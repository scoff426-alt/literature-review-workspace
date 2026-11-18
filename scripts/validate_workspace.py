from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

from common import (
    BODY_FIELDS,
    REVIEW_FIELDS,
    REVIEW_HEADERS,
    cards_path,
    inventory_path,
    parse_cards,
    pdfs,
    read_inventory,
    resolve_workspace,
    workbook_path,
    workspace_arg,
)


WORD_RANGES = {
    "Problem": (55, 90),
    "Object": (8, 25),
    "Constraints": (20, 45),
    "Model": (10, 30),
    "Solution": (40, 70),
    "Data": (20, 45),
    "Scale": (15, 50),
    "Results": (35, 65),
    "Innovation": (25, 80),
}
SOURCE_HINT = re.compile(
    r"(?:p\.|pp\.|page|pages|abstract|introduction|conclusion|sec\.|section|eq\.|fig\.|figure|table|algorithm|appendix)",
    re.IGNORECASE,
)
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*")
CJK_RE = re.compile(r"[\u3400-\u9fff]")
ACRONYM_RE = re.compile(r"\b[A-Z]{2,}(?:\d+)?\b")
SOURCE_ABBREVIATION_RE = re.compile(r"\b(?:p|pp|sec|fig|eq)\.", re.IGNORECASE)


@dataclass
class RunInfo:
    text: str
    bold: bool = False
    red: bool = False
    blue: bool = False


@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _rgb(color) -> str:
    if color is None or getattr(color, "type", None) != "rgb":
        return ""
    value = getattr(color, "rgb", "")
    return str(value).upper() if value else ""


def _is_red(color) -> bool:
    return _rgb(color).endswith("FF0000")


def _is_blue(color) -> bool:
    return _rgb(color).endswith("0000FF")


def cell_runs(cell) -> list[RunInfo]:
    try:
        from openpyxl.cell.rich_text import CellRichText, TextBlock
    except ImportError:
        CellRichText = ()  # type: ignore[assignment]
        TextBlock = ()  # type: ignore[assignment]

    value = cell.value
    if value is None:
        return []
    if isinstance(value, CellRichText):
        result: list[RunInfo] = []
        for part in value:
            if isinstance(part, TextBlock):
                result.append(
                    RunInfo(
                        text=part.text,
                        bold=bool(part.font.b),
                        red=_is_red(part.font.color),
                        blue=_is_blue(part.font.color),
                    )
                )
            else:
                result.append(RunInfo(text=str(part)))
        return result
    return [
        RunInfo(
            text=str(value),
            bold=bool(cell.font.bold),
            red=_is_red(cell.font.color),
            blue=_is_blue(cell.font.color),
        )
    ]


def _joined_text(runs: list[RunInfo]) -> str:
    return "".join(run.text for run in runs)


def _source_bounds(runs: list[RunInfo]) -> tuple[int, int, str] | None:
    text = _joined_text(runs)
    newline = text.rfind("\n")
    if newline < 0:
        return None
    source = text[newline + 1 :].strip()
    if not source.startswith("(") or not source.endswith(")") or not SOURCE_HINT.search(source):
        return None
    start = text.find(source, newline + 1)
    return start, start + len(source), source


def source_run_is_valid(runs: list[RunInfo]) -> bool:
    bounds = _source_bounds(runs)
    if bounds is None:
        return False
    start, end, _ = bounds
    cursor = 0
    covered = 0
    for run in runs:
        run_start = cursor
        run_end = cursor + len(run.text)
        overlap = max(0, min(end, run_end) - max(start, run_start))
        if overlap:
            covered += overlap
            if not run.blue or run.bold or run.red:
                return False
        cursor = run_end
    return covered == end - start


def _body_runs(runs: list[RunInfo]) -> list[RunInfo]:
    bounds = _source_bounds(runs)
    if bounds is None:
        return runs
    start, _, _ = bounds
    result: list[RunInfo] = []
    cursor = 0
    for run in runs:
        run_start = cursor
        run_end = cursor + len(run.text)
        if run_start >= start:
            break
        keep = min(len(run.text), start - run_start)
        if keep > 0:
            result.append(RunInfo(run.text[:keep], run.bold, run.red, run.blue))
        cursor = run_end
    return result


def _focus_is_long_enough(text: str) -> bool:
    text = text.strip()
    if not text:
        return False
    if CJK_RE.search(text):
        return len(CJK_RE.findall(text)) >= 8
    return len(WORD_RE.findall(text)) >= 4


def meaningful_focus(runs: list[RunInfo], *, red: bool) -> bool:
    for run in _body_runs(runs):
        if run.bold and run.red == red and _focus_is_long_enough(run.text):
            return True
    return False


def _body_has_red(runs: list[RunInfo]) -> bool:
    return any(run.red and run.text.strip() for run in _body_runs(runs))


def _body_word_count(runs: list[RunInfo]) -> int:
    return len(WORD_RE.findall(_joined_text(_body_runs(runs))))


def undefined_acronyms(text: str) -> list[str]:
    """Return acronyms whose first occurrence is not introduced as Full Name (ABC)."""
    undefined: list[str] = []
    seen: set[str] = set()
    for match in ACRONYM_RE.finditer(text):
        acronym = match.group(0)
        if acronym in seen:
            continue
        seen.add(acronym)
        start, end = match.span()
        parenthesized = start > 0 and end < len(text) and text[start - 1] == "(" and text[end] == ")"
        if parenthesized:
            prefix = text[: start - 1]
            phrase = re.split(r"[.;:\n]", prefix)[-1]
            words = re.findall(r"[A-Za-z][A-Za-z-]*", phrase)
            if len(words) >= 2:
                continue
        undefined.append(acronym)
    return undefined


def _headers(ws) -> list[str]:
    return [str(ws.cell(1, col).value or "").strip() for col in range(1, len(REVIEW_HEADERS) + 1)]


def validate_review_workbook(path: str | Path) -> ValidationReport:
    report = ValidationReport()
    xlsx = Path(path)
    if not xlsx.exists():
        report.errors.append(f"工作簿不存在: {xlsx}")
        return report
    try:
        from openpyxl import load_workbook
    except ImportError:
        report.errors.append("openpyxl 不可用，无法检查 Excel 富文本。")
        return report

    try:
        wb = load_workbook(xlsx, read_only=False, data_only=False, rich_text=True)
    except Exception as exc:  # openpyxl exposes several format-specific exceptions
        report.errors.append(f"工作簿无法打开: {exc}")
        return report

    ws = wb.active
    headers = _headers(ws)
    if headers != REVIEW_HEADERS:
        report.errors.append(
            "16 列表头或顺序不正确；应为: " + " / ".join(REVIEW_HEADERS)
        )
        report.stats.update(
            {
                "workbook": str(xlsx),
                "sheet": ws.title,
                "headers": headers,
                "images": len(getattr(ws, "_images", [])),
            }
        )
        return report

    header_to_col = {header: index + 1 for index, header in enumerate(headers)}
    title_col = header_to_col["Title"]
    rows = [
        row
        for row in range(2, ws.max_row + 1)
        if str(ws.cell(row, title_col).value or "").strip()
    ]
    if not rows:
        report.errors.append("工作簿没有论文正文行。")

    image_count = len(getattr(ws, "_images", []))
    if image_count:
        report.errors.append(f"工作簿包含 {image_count} 张内嵌图片；当前模板要求 0 张。")

    comment_count = 0
    coverage = {field: 0 for field in REVIEW_FIELDS}
    source_coverage = {field: 0 for field in REVIEW_FIELDS}
    for row in rows:
        category_cell = ws.cell(row, header_to_col["类别"])
        if any(run.bold and run.text.strip() for run in cell_runs(category_cell)):
            report.errors.append(f"第 {row} 行 类别: 类别单元格不应加粗。")

        keyword_runs = cell_runs(ws.cell(row, header_to_col["关键词"]))
        keyword_bold_runs = [run for run in keyword_runs if run.bold and run.text.strip()]
        if len(keyword_bold_runs) > 2:
            report.warnings.append(f"第 {row} 行 关键词: 加粗片段超过 2 处。")

        for field_name in ["类别", "关键词"]:
            field_text = _joined_text(cell_runs(ws.cell(row, header_to_col[field_name])))
            for acronym in undefined_acronyms(field_text):
                report.errors.append(
                    f"第 {row} 行 {field_name}: 缩写 {acronym} 首次出现时缺少全称；应写为 Full Name ({acronym})。"
                )

        for cell in ws[row]:
            if cell.comment is not None:
                comment_count += 1

        for field_name in REVIEW_FIELDS:
            cell = ws.cell(row, header_to_col[field_name])
            text = str(cell.value or "").strip()
            if not text:
                report.errors.append(f"第 {row} 行 {field_name}: 字段为空。")
                continue
            runs = cell_runs(cell)
            if source_run_is_valid(runs):
                source_coverage[field_name] += 1
                bounds = _source_bounds(runs)
                if bounds is not None and SOURCE_ABBREVIATION_RE.search(bounds[2]):
                    report.errors.append(
                        f"第 {row} 行 {field_name}: 来源定位不要使用 p./pp./Sec./Fig./Eq.，请写完整的 page/pages/Section/Figure/Equation。"
                    )
            else:
                report.errors.append(
                    f"第 {row} 行 {field_name}: 缺少蓝色来源位置（必须换行、括号且不加粗）。"
                )

            for acronym in undefined_acronyms(_joined_text(runs)):
                report.errors.append(
                    f"第 {row} 行 {field_name}: 缩写 {acronym} 首次出现时缺少全称；应写为 Full Name ({acronym})。"
                )

            if field_name == "Innovation":
                if meaningful_focus(runs, red=True):
                    coverage[field_name] += 1
                else:
                    report.errors.append(
                        f"第 {row} 行 Innovation: 没有语义完整的红色加粗创新点。"
                    )
            else:
                if _body_has_red(runs):
                    report.errors.append(f"第 {row} 行 {field_name}: 非 Innovation 字段不应使用红色。")
                if meaningful_focus(runs, red=False):
                    coverage[field_name] += 1
                else:
                    report.errors.append(
                        f"第 {row} 行 {field_name}: 缺少黑色加粗重点，或重点片段过短。"
                    )

            count = _body_word_count(runs)
            low, high = WORD_RANGES[field_name]
            if count < low or count > high:
                report.warnings.append(
                    f"第 {row} 行 {field_name}: 正文约 {count} 个英文单词，参考范围为 {low}-{high}。"
                )

    if comment_count:
        report.errors.append(f"工作簿包含 {comment_count} 个 Excel 注释；当前模板要求 0 个。")

    report.stats.update(
        {
            "workbook": str(xlsx),
            "sheet": ws.title,
            "rows": len(rows),
            "columns": len(headers),
            "images": image_count,
            "comments": comment_count,
            "focus_coverage": coverage,
            "source_coverage": source_coverage,
        }
    )
    return report


def _validate_workspace_artifacts(workspace: Path, report: ValidationReport, final: bool) -> None:
    inventory = read_inventory(inventory_path(workspace))
    cards = parse_cards(cards_path(workspace))
    pdf_count = len(pdfs(workspace))
    report.stats.update(
        {
            "pdfs": pdf_count,
            "inventory_rows": len(inventory),
            "knowledge_cards": len(cards),
        }
    )

    if not inventory:
        (report.errors if final else report.warnings).append("source_inventory.csv 不存在或为空。")
    if not cards_path(workspace).exists():
        (report.errors if final else report.warnings).append("知识卡片.md 不存在。")

    ids = [row.get("Paper ID", "") for row in inventory if row.get("Paper ID")]
    duplicate_ids = [pid for pid, count in Counter(ids).items() if count > 1]
    if duplicate_ids:
        report.errors.append(f"Paper ID 重复: {', '.join(duplicate_ids)}")

    for row in inventory:
        pid = row.get("Paper ID", "") or "(未编号)"
        pdf_file = row.get("PDF File", "")
        if not pdf_file:
            (report.errors if final else report.warnings).append(f"{pid}: 缺 PDF File。")
        elif final and not (workspace / pdf_file).exists():
            report.errors.append(f"{pid}: PDF File 指向的文件不存在: {pdf_file}")
        if final and row.get("Language", "").strip().lower() != "english":
            report.errors.append(f"{pid}: Language 必须为 English。")
        if final and not row.get("中科院分区", "").strip():
            report.warnings.append(f"{pid}: 缺少中科院分区。")


def main() -> None:
    parser = workspace_arg()
    parser.add_argument("--workbook", default="", help="要检查的 xlsx 路径。")
    parser.add_argument("--final", action="store_true", help="同时启用 PDF、语言和知识卡片最终门禁。")
    parser.add_argument("--json-report", default="", help="可选的 JSON 报告路径。")
    args = parser.parse_args()

    workspace = resolve_workspace(args.workspace)
    xlsx = resolve_workspace(args.workbook) if args.workbook else workbook_path(workspace)
    report = validate_review_workbook(xlsx)
    _validate_workspace_artifacts(workspace, report, args.final)

    print("Validation result")
    print(f"- Workbook: {xlsx}")
    print(f"- Rows: {report.stats.get('rows', 0)}")
    print(f"- Errors: {len(report.errors)}")
    print(f"- Warnings: {len(report.warnings)}")
    if report.errors:
        print("\nErrors:")
        for item in report.errors:
            print(f"- {item}")
    if report.warnings:
        print("\nWarnings:")
        for item in report.warnings:
            print(f"- {item}")

    if args.json_report:
        output = resolve_workspace(args.json_report)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"- JSON report: {output}")

    if report.errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
