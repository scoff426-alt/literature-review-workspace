from __future__ import annotations

from pathlib import Path

from common import cards_path, inventory_path, parse_cards, read_inventory, resolve_workspace, workbook_path, workspace_arg


SUMMARY_FIELDS = [
    "Problem",
    "Object",
    "Constraints",
    "Model",
    "Solution",
    "Data",
    "Scale",
    "Results",
    "Innovation",
    "Limitations",
    "Review Use",
    "Related Papers",
]

REQUIRED_SUMMARY_FIELDS = {"Object", "Constraints", "Model", "Data", "Scale"}

SUMMARY_FIELD_ALIASES = {
    "Problem": ("Problem",),
    "Object": ("Object",),
    "Constraints": ("Constraints",),
    "Model": ("Model", "Model / Method"),
    "Solution": ("Solution",),
    "Data": ("Data", "Data / Setting"),
    "Scale": ("Scale", "Scale / Object"),
    "Results": ("Results",),
    "Innovation": ("Innovation",),
    "Limitations": ("Limitations",),
    "Review Use": ("Review Use",),
    "Related Papers": ("Related Papers",),
}

HEADERS = [
    "Paper ID",
    "Row Type",
    "类别",
    "日期",
    "关键词",
    "authors",
    "journal",
    "Year",
    "Title",
    "DOI",
    "PDF File",
    "Evidence / Screenshot",
    *SUMMARY_FIELDS,
]


def main() -> None:
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font, PatternFill
        from openpyxl.utils import get_column_letter
    except ImportError as exc:
        raise SystemExit("openpyxl is required to build 文献综述.xlsx. Install openpyxl or run inside the Codex Python runtime.") from exc

    parser = workspace_arg()
    parser.add_argument("--output", default="", help="输出 xlsx 路径，默认工作区/文献综述.xlsx。")
    args = parser.parse_args()
    workspace = resolve_workspace(args.workspace)
    rows = read_inventory(inventory_path(workspace))
    cards = parse_cards(cards_path(workspace))

    wb = Workbook()
    ws = wb.active
    ws.title = "Literature Review"
    ws.append(HEADERS)

    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)
    summary_fill = PatternFill("solid", fgColor="EAF7EA")
    evidence_fill = PatternFill("solid", fgColor="FDF2E9")
    source_fill = PatternFill("solid", fgColor="EAF2F8")

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for item in rows:
        pid = item.get("Paper ID", "")
        card = cards.get(pid, {})
        authors_year = item.get("Authors / Year", "")
        authors, year = split_authors_year(authors_year)
        doi = normalize_doi(item.get("DOI", ""))
        base = {
            "Paper ID": pid,
            "类别": item.get("Category", ""),
            "日期": item.get("Date", ""),
            "关键词": item.get("Keywords", ""),
            "authors": item.get("Authors", "") or authors,
            "journal": item.get("Venue", ""),
            "Year": item.get("Year", "") or year,
            "Title": item.get("Title", ""),
            "DOI": doi,
            "PDF File": item.get("PDF File", ""),
        }
        summary = {**base, "Row Type": "Summary"}
        for field in SUMMARY_FIELDS:
            value = first_card_value(card, SUMMARY_FIELD_ALIASES[field])
            if not value and field in REQUIRED_SUMMARY_FIELDS:
                value = "Not clearly specified in the paper."
            summary[field] = value
        append_row(ws, summary)
        append_row(ws, {"Paper ID": pid, "Row Type": "Evidence", "Evidence / Screenshot": build_evidence_template(pid)})
        append_row(ws, {"Paper ID": pid, "Row Type": "Source", "DOI": doi, "PDF File": item.get("PDF File", "")})

    for row in ws.iter_rows(min_row=2):
        row_type = row[1].value
        fill = summary_fill if row_type == "Summary" else evidence_fill if row_type == "Evidence" else source_fill
        for cell in row:
            cell.fill = fill
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        if row_type in {"Summary", "Source"}:
            doi_cell = row[HEADERS.index("DOI")]
            if doi_cell.value:
                doi_cell.hyperlink = f"https://doi.org/{doi_cell.value}"
                doi_cell.style = "Hyperlink"
        if row_type == "Summary":
            # Summary 保留除 DOI、PDF File、Evidence / Screenshot 以外的全部内容。
            for field in ["DOI", "PDF File", "Evidence / Screenshot"]:
                row[HEADERS.index(field)].value = ""
                row[HEADERS.index(field)].hyperlink = None
            for idx in [13, 16, 19, 20, 21, 22]:
                if idx <= len(row) and row[idx - 1].value:
                    row[idx - 1].font = Font(bold=True)
        elif row_type == "Evidence":
            # Evidence 只保留截图或截图位置说明，避免与 Summary/Source 重复。
            for idx, header in enumerate(HEADERS):
                if header not in {"Paper ID", "Row Type", "Evidence / Screenshot"}:
                    row[idx].value = ""
                    row[idx].hyperlink = None
        elif row_type == "Source":
            # Source 只保留 DOI 和 PDF File。
            for idx, header in enumerate(HEADERS):
                if header not in {"Paper ID", "Row Type", "DOI", "PDF File"}:
                    row[idx].value = ""
                    row[idx].hyperlink = None

    widths = {
        "A": 10,
        "B": 12,
        "C": 16,
        "D": 14,
        "E": 24,
        "F": 26,
        "G": 24,
        "H": 12,
        "I": 42,
        "J": 24,
        "K": 34,
        "L": 34,
    }
    for col_idx in range(1, len(HEADERS) + 1):
        letter = get_column_letter(col_idx)
        ws.column_dimensions[letter].width = widths.get(letter, 28)
    for row_idx in range(2, ws.max_row + 1):
        ws.row_dimensions[row_idx].height = 54
    ws.row_dimensions[1].height = 36
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    add_category_summary(wb, rows)

    output = Path(args.output).resolve() if args.output else workbook_path(workspace)
    output.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output)
    print(f"Built workbook: {output}")


def append_row(ws, values: dict[str, str]) -> None:
    ws.append([values.get(header, "") for header in HEADERS])


def normalize_doi(value: str) -> str:
    doi = (value or "").strip()
    doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
    if doi.lower().startswith("doi:"):
        doi = doi[4:].strip()
    return doi


def split_authors_year(value: str) -> tuple[str, str]:
    text = (value or "").strip()
    if "/" in text:
        authors, year = text.rsplit("/", 1)
        return authors.strip(), year.strip()
    if "," in text:
        authors, year = text.rsplit(",", 1)
        if year.strip().isdigit():
            return authors.strip(), year.strip()
    return text, ""


def first_card_value(card: dict[str, str], aliases: tuple[str, ...]) -> str:
    for alias in aliases:
        value = card.get(alias, "")
        if value:
            return value
    return ""


def build_evidence_template(pid: str) -> str:
    lines = []
    for field in SUMMARY_FIELDS:
        slug = field.lower().replace(" ", "_")
        lines.append(f"{field}: evidence_images/{pid}_{slug}.png; p./Sec. ; field-specific screenshot")
    return "\n".join(lines)


def add_category_summary(wb, rows: list[dict[str, str]]) -> None:
    from openpyxl.styles import Font

    ws = wb.create_sheet("Category Summary")
    ws.append(["Category", "Count", "Paper IDs"])
    grouped: dict[str, list[str]] = {}
    for row in rows:
        category = row.get("Category") or "Uncategorized"
        grouped.setdefault(category, []).append(row.get("Paper ID", ""))
    for category, ids in sorted(grouped.items()):
        ws.append([category, len(ids), ", ".join(pid for pid in ids if pid)])
    for cell in ws[1]:
        cell.font = Font(bold=True)


if __name__ == "__main__":
    main()
