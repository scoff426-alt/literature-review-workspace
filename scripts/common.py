from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path


INVENTORY_NAME = "source_inventory.csv"
CARDS_NAME = "知识卡片.md"
WORKBOOK_NAME = "文献综述.xlsx"

PDF_DIR = "papers"
OUTPUT_DIR = "outputs"

REVIEW_HEADERS = [
    "日期",
    "类别",
    "关键词",
    "authors",
    "journal",
    "Year",
    "Title",
    "Problem",
    "Object",
    "Constraints",
    "Model",
    "Solution",
    "Data",
    "Scale",
    "Results",
    "Innovation",
]
REVIEW_FIELDS = REVIEW_HEADERS[7:]
BODY_FIELDS = REVIEW_FIELDS[:-1]


@dataclass
class InventoryRow:
    paper_id: str
    title: str
    authors_year: str
    venue: str
    language: str
    cas_partition: str
    quality_rank: str
    relevance_note: str
    doi: str
    source_url: str
    pdf_file: str
    category: str
    keywords: str
    status: str
    notes: str


INVENTORY_FIELDS = [
    "Paper ID",
    "Title",
    "Authors / Year",
    "Venue",
    "Language",
    "中科院分区",
    "Quality Rank",
    "Relevance Note",
    "DOI",
    "Source URL",
    "PDF File",
    "Category",
    "Keywords",
    "Status",
    "Notes",
]


def workspace_arg() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "workspace",
        nargs="?",
        default=".",
        help="文献综述工作区路径，默认当前目录。",
    )
    return parser


def resolve_workspace(value: str) -> Path:
    return Path(value).expanduser().resolve()


def ensure_workspace_dirs(workspace: Path) -> None:
    for name in (PDF_DIR, OUTPUT_DIR):
        (workspace / name).mkdir(parents=True, exist_ok=True)


def slug_from_pdf(path: Path) -> str:
    stem = path.stem
    stem = re.sub(r"^\d+[_\-\s]+", "", stem)
    stem = stem.replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", stem).strip()


def paper_id(index: int) -> str:
    return f"{index:02d}"


def read_inventory(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            rows.append({field: (row.get(field) or "").strip() for field in INVENTORY_FIELDS})
        return rows


def write_inventory(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=INVENTORY_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in INVENTORY_FIELDS})


def inventory_path(workspace: Path) -> Path:
    return workspace / INVENTORY_NAME


def workbook_path(workspace: Path) -> Path:
    canonical = workspace / WORKBOOK_NAME
    if canonical.exists():
        return canonical
    candidates = sorted(
        workspace.glob("文献综述*.xlsx"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else canonical


def cards_path(workspace: Path) -> Path:
    return workspace / CARDS_NAME


def pdfs(workspace: Path) -> list[Path]:
    found = list((workspace / PDF_DIR).glob("*.pdf")) if (workspace / PDF_DIR).exists() else []
    found.extend(workspace.glob("*.pdf"))
    return sorted({path.resolve(): path for path in found}.values())


def parse_cards(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8-sig")
    sections = re.split(r"(?m)^##\s+(\d+)\.\s+(.+?)\s*$", text)
    cards: dict[str, dict[str, str]] = {}
    for i in range(1, len(sections), 3):
        pid = sections[i].strip()
        title = sections[i + 1].strip()
        body = sections[i + 2]
        cards[pid] = {
            "Title": title,
            "Authors / Year": extract_bullet(body, "Authors / Year"),
            "Venue": extract_bullet(body, "Venue"),
            "Language": extract_bullet(body, "Language"),
            "中科院分区": extract_bullet(body, "中科院分区"),
            "DOI": extract_bullet(body, "DOI"),
            "PDF File": extract_bullet(body, "File"),
            "Category": extract_bullet(body, "Category"),
            "Keywords": extract_bullet(body, "Keywords"),
            "Problem": extract_bullet(body, "研究问题"),
            "Object": "",
            "Constraints": "",
            "Model / Method": extract_bullet(body, "方法"),
            "Solution": extract_bullet(body, "核心思路"),
            "Data / Setting": extract_bullet(body, "数据 / 场景"),
            "Scale / Object": extract_bullet(body, "规模 / 对象"),
            "Results": extract_bullet(body, "主要结论"),
            "Innovation": extract_bullet(body, "可复用观点"),
            "Limitations": extract_bullet(body, "局限"),
            "Review Use": extract_bullet(body, "适合综述位置"),
            "Related Papers": extract_bullet(body, "可连接文献"),
        }
    return cards


def extract_bullet(body: str, label: str) -> str:
    pattern = rf"(?m)^-\s*{re.escape(label)}\s*[:：]\s*(.*)$"
    match = re.search(pattern, body)
    return match.group(1).strip() if match else ""
