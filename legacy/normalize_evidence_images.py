from __future__ import annotations

import re
import shutil
from pathlib import Path

from common import resolve_workspace, workbook_path, workspace_arg


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


def main() -> None:
    try:
        from openpyxl import load_workbook
        from openpyxl.drawing.image import Image
    except ImportError as exc:
        raise SystemExit("openpyxl and pillow are required to normalize evidence images.") from exc

    parser = workspace_arg()
    parser.add_argument("--workbook", default="", help="要处理的 xlsx 路径，默认工作区/文献综述.xlsx。")
    parser.add_argument("--output", default="", help="输出 xlsx 路径，默认写入工作区/outputs/。")
    parser.add_argument("--in-place", action="store_true", help="直接覆盖输入工作簿；仅在用户明确确认后使用。")
    args = parser.parse_args()

    workspace = resolve_workspace(args.workspace)
    xlsx = resolve_workspace(args.workbook) if args.workbook else workbook_path(workspace)
    if args.output:
        output = resolve_workspace(args.output)
    elif args.in_place:
        output = xlsx
    else:
        output = workspace / "outputs" / f"{xlsx.stem}_evidence_normalized.xlsx"
    evidence_dir = workspace / "evidence_images"

    wb = load_workbook(xlsx)
    ws = wb["Literature Review"] if "Literature Review" in wb.sheetnames else wb.active
    headers = {cell.value: idx + 1 for idx, cell in enumerate(ws[1])}
    reverse_headers = {idx + 1: cell.value for idx, cell in enumerate(ws[1])}
    evidence_col = headers["Evidence / Screenshot"]

    ws._images = []
    normalized_count = 0
    missing: list[str] = []

    for row in ws.iter_rows(min_row=2):
        pid = str(row[headers["Paper ID"] - 1].value or "").strip()
        row_type = str(row[headers["Row Type"] - 1].value or "").strip()
        if row_type != "Evidence" or not pid:
            continue

        evidence_cell = row[evidence_col - 1]
        evidence_text = str(evidence_cell.value or "")
        field_paths = build_field_specific_paths(pid, evidence_text, evidence_dir, missing)
        evidence_cell.value = rewrite_evidence_text(pid, evidence_text, field_paths)

        for field, image_path in field_paths.items():
            if field not in headers or not image_path.exists():
                continue
            img = Image(str(image_path))
            img.width = 220
            img.height = 300
            anchor = f"{column_letter(headers[field])}{row[0].row}"
            ws.add_image(img, anchor)
            normalized_count += 1
        ws.row_dimensions[row[0].row].height = max(ws.row_dimensions[row[0].row].height or 0, 240)

    output.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output)
    print(f"Normalized evidence images: {normalized_count}")
    print(f"Workbook: {output}")
    if missing:
        print("Missing evidence image sources:")
        for item in missing:
            print(f"- {item}")
    print("Image anchors are now field-column based:")
    for field in SUMMARY_FIELDS:
        if field in headers:
            print(f"- {field}: column {column_letter(headers[field])}")


def build_field_specific_paths(pid: str, evidence_text: str, evidence_dir: Path, missing: list[str]) -> dict[str, Path]:
    field_paths: dict[str, Path] = {}
    for field in SUMMARY_FIELDS:
        source = first_image_path(field_line(evidence_text, field), evidence_dir)
        if source is None:
            missing.append(f"{pid} {field}: no screenshot path found")
            continue
        if not source.exists():
            missing.append(f"{pid} {field}: {source}")
            continue
        target = evidence_dir / f"{pid}_{slug(field)}.png"
        if source.resolve() != target.resolve():
            shutil.copyfile(source, target)
        field_paths[field] = target
    return field_paths


def rewrite_evidence_text(pid: str, evidence_text: str, field_paths: dict[str, Path]) -> str:
    lines: list[str] = []
    for field in SUMMARY_FIELDS:
        line = field_line(evidence_text, field)
        location = extract_location(line)
        path = field_paths.get(field)
        if path is None:
            lines.append(f"{field}: No direct screenshot; checked section/page from existing evidence.")
        else:
            rel = f"evidence_images/{path.name}"
            suffix = f"; {location}" if location else ""
            lines.append(f"{field}: {rel}{suffix}; field-specific screenshot for {field}.")
    return "\n".join(lines)


def field_line(text: str, field: str) -> str:
    pattern = re.compile(rf"(^|[\n\r])\s*{re.escape(field)}\s*:\s*(.*?)(?=(\n\s*(?:{'|'.join(re.escape(f) for f in SUMMARY_FIELDS)})\s*:)|\Z)", re.IGNORECASE | re.DOTALL)
    match = pattern.search(text or "")
    return match.group(2).strip() if match else ""


def first_image_path(text: str, evidence_dir: Path) -> Path | None:
    match = re.search(r"evidence_images[/\\]([^;\n\r,，]+?\.(?:png|jpg|jpeg))", text or "", re.IGNORECASE)
    if not match:
        return None
    return evidence_dir / match.group(1)


def extract_location(line: str) -> str:
    cleaned = re.sub(r"screenshots?:.*", "", line or "", flags=re.IGNORECASE).strip(" ;")
    cleaned = re.sub(r"screenshot:.*", "", cleaned, flags=re.IGNORECASE).strip(" ;")
    return cleaned


def slug(field: str) -> str:
    return field.lower().replace(" ", "_")


def column_letter(idx: int) -> str:
    letters = ""
    while idx:
        idx, rem = divmod(idx - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


if __name__ == "__main__":
    main()
