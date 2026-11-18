from __future__ import annotations

import re
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
        from openpyxl.drawing.image import Image as XlsxImage
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise SystemExit("openpyxl and pillow are required to highlight evidence screenshots.") from exc

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
        output = workspace / "outputs" / f"{xlsx.stem}_highlighted.xlsx"

    wb = load_workbook(xlsx)
    ws = wb["Literature Review"] if "Literature Review" in wb.sheetnames else wb.active
    headers = {cell.value: idx + 1 for idx, cell in enumerate(ws[1])}
    evidence_col = headers["Evidence / Screenshot"]
    evidence_dir = workspace / "evidence_images"

    ws._images = []
    highlighted_count = 0
    missing: list[str] = []

    for row in ws.iter_rows(min_row=2):
        pid = str(row[headers["Paper ID"] - 1].value or "").strip()
        row_type = str(row[headers["Row Type"] - 1].value or "").strip()
        if row_type != "Evidence" or not pid:
            continue

        evidence_cell = row[evidence_col - 1]
        evidence_text = str(evidence_cell.value or "")
        replacements: dict[str, str] = {}

        for field in SUMMARY_FIELDS:
            source = first_image_path(field_line(evidence_text, field), evidence_dir)
            if source is None:
                missing.append(f"{pid} {field}: no screenshot path found")
                continue
            if not source.exists():
                missing.append(f"{pid} {field}: {source}")
                continue

            target = highlighted_path(source)
            create_highlighted_image(source, target, Image, ImageDraw)
            replacements[source.name] = target.name

            if field in headers:
                ximg = XlsxImage(str(target))
                ximg.width = 220
                ximg.height = 300
                ws.add_image(ximg, f"{column_letter(headers[field])}{row[0].row}")
                highlighted_count += 1

        for old_name, new_name in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
            evidence_text = evidence_text.replace(f"evidence_images/{old_name}", f"evidence_images/{new_name}")
            evidence_text = evidence_text.replace(f"evidence_images\\{old_name}", f"evidence_images/{new_name}")
        evidence_cell.value = evidence_text
        ws.row_dimensions[row[0].row].height = max(ws.row_dimensions[row[0].row].height or 0, 240)

    output.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output)
    print(f"Highlighted screenshots embedded: {highlighted_count}")
    print(f"Workbook: {output}")
    if missing:
        print("Missing screenshot sources:")
        for item in missing:
            print(f"- {item}")


def create_highlighted_image(source: Path, target: Path, image_module, draw_module) -> None:
    img = image_module.open(source).convert("RGBA")
    overlay = image_module.new("RGBA", img.size, (255, 255, 255, 0))
    draw = draw_module.Draw(overlay)
    for box in locate_evidence_boxes(img):
        draw.rounded_rectangle(box, radius=6, fill=(255, 236, 80, 72), outline=(230, 160, 20, 210), width=3)
    result = image_module.alpha_composite(img, overlay).convert("RGB")
    target.parent.mkdir(parents=True, exist_ok=True)
    result.save(target, quality=95)


def locate_evidence_boxes(img) -> list[tuple[int, int, int, int]]:
    width, height = img.size
    gray = img.convert("L")
    pixels = gray.load()
    x_min_scan = int(width * 0.05)
    x_max_scan = int(width * 0.95)
    y_min_scan = int(height * 0.08)
    y_max_scan = int(height * 0.92)
    threshold = max(8, int(width * 0.006))

    active_rows: list[int] = []
    for y in range(y_min_scan, y_max_scan):
        dark = 0
        for x in range(x_min_scan, x_max_scan, 3):
            if pixels[x, y] < 185:
                dark += 1
        if dark >= threshold:
            active_rows.append(y)

    groups = group_positions(active_rows, max_gap=max(8, int(height * 0.012)))
    candidates: list[tuple[int, int, int, int, int]] = []
    for y1, y2 in groups:
        if y2 - y1 < max(12, int(height * 0.012)):
            continue
        x1, x2, dark_count = horizontal_bounds(pixels, width, y1, y2)
        if dark_count < 20:
            continue
        pad_x = int(width * 0.015)
        pad_y = int(height * 0.008)
        box = (
            max(0, x1 - pad_x),
            max(0, y1 - pad_y),
            min(width - 1, x2 + pad_x),
            min(height - 1, y2 + pad_y),
            dark_count,
        )
        candidates.append(box)

    candidates.sort(key=lambda item: item[4] * max(1, item[3] - item[1]), reverse=True)
    selected: list[tuple[int, int, int, int]] = []
    for x1, y1, x2, y2, _ in candidates:
        if len(selected) >= 2:
            break
        if y2 - y1 > height * 0.38:
            y2 = int(y1 + height * 0.38)
        box = (x1, y1, x2, y2)
        if not any(overlap_ratio(box, old) > 0.25 for old in selected):
            selected.append(box)

    if selected:
        return selected
    return [(int(width * 0.08), int(height * 0.25), int(width * 0.92), int(height * 0.45))]


def group_positions(values: list[int], max_gap: int) -> list[tuple[int, int]]:
    if not values:
        return []
    groups: list[tuple[int, int]] = []
    start = prev = values[0]
    for value in values[1:]:
        if value - prev > max_gap:
            groups.append((start, prev))
            start = value
        prev = value
    groups.append((start, prev))
    return groups


def horizontal_bounds(pixels, width: int, y1: int, y2: int) -> tuple[int, int, int]:
    columns: list[int] = []
    dark_total = 0
    for x in range(int(width * 0.04), int(width * 0.96), 2):
        dark = 0
        for y in range(y1, y2 + 1, 3):
            if pixels[x, y] < 185:
                dark += 1
        if dark:
            columns.append(x)
            dark_total += dark
    if not columns:
        return int(width * 0.08), int(width * 0.92), 0
    return min(columns), max(columns), dark_total


def overlap_ratio(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0
    inter = (ix2 - ix1) * (iy2 - iy1)
    area = min((ax2 - ax1) * (ay2 - ay1), (bx2 - bx1) * (by2 - by1))
    return inter / area if area else 0.0


def highlighted_path(source: Path) -> Path:
    if source.stem.endswith("_highlighted"):
        return source
    return source.with_name(f"{source.stem}_highlighted{source.suffix}")


def field_line(text: str, field: str) -> str:
    pattern = re.compile(rf"(^|[\n\r])\s*{re.escape(field)}\s*:\s*(.*?)(?=(\n\s*(?:{'|'.join(re.escape(f) for f in SUMMARY_FIELDS)})\s*:)|\Z)", re.IGNORECASE | re.DOTALL)
    match = pattern.search(text or "")
    return match.group(2).strip() if match else ""


def first_image_path(text: str, evidence_dir: Path) -> Path | None:
    match = re.search(r"evidence_images[/\\]([^;\n\r,，]+?\.(?:png|jpg|jpeg))", text or "", re.IGNORECASE)
    if not match:
        return None
    return evidence_dir / match.group(1)


def column_letter(idx: int) -> str:
    letters = ""
    while idx:
        idx, rem = divmod(idx - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


if __name__ == "__main__":
    main()
