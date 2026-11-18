from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import validate_workspace as validator


HEADERS = [
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
FIELDS = HEADERS[7:]


def review_text(
    body: str,
    emphasis: str,
    source: str = "(page 1, Abstract)",
    *,
    innovation: bool = False,
    red_override: bool | None = None,
) -> CellRichText:
    normal = InlineFont(rFont="Microsoft YaHei", color="FF000000")
    red = innovation if red_override is None else red_override
    focus = InlineFont(
        rFont="Microsoft YaHei",
        b=True,
        color="FFFF0000" if red else "FF000000",
    )
    blue = InlineFont(rFont="Microsoft YaHei", color="FF0000FF")
    before, after = body.split(emphasis, 1)
    return CellRichText(
        TextBlock(normal, before),
        TextBlock(focus, emphasis),
        TextBlock(normal, after),
        TextBlock(blue, "\n" + source),
    )


def create_valid_workbook(path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "文献综述"
    ws.append(HEADERS)
    ws.append(
        [
            "2026-07-14",
            "空箱调运",
            "empty container repositioning; stochastic demand",
            "A. Author; B. Author",
            "Transportation Research Part E",
            2025,
            "A representative paper title",
        ]
        + [None] * len(FIELDS)
    )
    bodies = {
        "Problem": (
            "Existing allocation studies overlook the operational coupling between empty-container availability and sequential cargo demand.",
            "operational coupling between empty-container availability and sequential cargo demand",
        ),
        "Object": (
            "The study object is liner-shipping slot allocation with empty-container repositioning.",
            "liner-shipping slot allocation with empty-container repositioning",
        ),
        "Constraints": (
            "Decisions must respect slot capacity, inventory balance, and sequential demand revelation.",
            "slot capacity, inventory balance, and sequential demand revelation",
        ),
        "Model": (
            "The model couples stochastic dynamic programming with an approximate value function.",
            "stochastic dynamic programming with an approximate value function",
        ),
        "Solution": (
            "The authors decompose the decision process and solve it with an approximate dynamic programming procedure.",
            "decompose the decision process and solve it with an approximate dynamic programming procedure",
        ),
        "Data": (
            "Inputs comprise booking demand, slot capacity, and empty-container inventory records.",
            "booking demand, slot capacity, and empty-container inventory records",
        ),
        "Scale": (
            "The experiments cover multiple demand scenarios, vessel legs, and inventory configurations.",
            "multiple demand scenarios, vessel legs, and inventory configurations",
        ),
        "Results": (
            "The method improves expected profit while reducing infeasible accepted bookings in the tested scenarios.",
            "improves expected profit while reducing infeasible accepted bookings",
        ),
        "Innovation": (
            "The main innovation is jointly modelling sequential cargo acceptance and empty-container availability.",
            "jointly modelling sequential cargo acceptance and empty-container availability",
        ),
    }
    for col, field in enumerate(FIELDS, start=8):
        body, emphasis = bodies[field]
        ws.cell(2, col).value = review_text(body, emphasis, innovation=field == "Innovation")
    wb.save(path)


class ValidateWorkspaceTests(unittest.TestCase):
    def setUp(self) -> None:
        test_root = Path(os.environ.get("LITERATURE_REVIEW_TEST_TMP", tempfile.gettempdir()))
        test_root.mkdir(parents=True, exist_ok=True)
        self.path = test_root / f"literature_review_{os.getpid()}_{self._testMethodName}.xlsx"
        self.path.unlink(missing_ok=True)
        create_valid_workbook(self.path)

    def tearDown(self) -> None:
        self.path.unlink(missing_ok=True)

    def validate(self):
        fn = getattr(validator, "validate_review_workbook", None)
        self.assertIsNotNone(fn, "validate_review_workbook must implement the current 16-column contract")
        return fn(self.path)

    def test_valid_current_template_has_no_errors(self):
        report = self.validate()
        self.assertEqual([], report.errors)

    def test_missing_header_fails(self):
        wb = load_workbook(self.path, rich_text=True)
        ws = wb.active
        ws["P1"] = "InnovationX"
        wb.save(self.path)
        report = self.validate()
        self.assertTrue(any("16 列表头" in item for item in report.errors))

    def test_missing_blue_source_fails(self):
        wb = load_workbook(self.path, rich_text=True)
        ws = wb.active
        ws["H2"] = "A problem statement without a blue source position."
        wb.save(self.path)
        report = self.validate()
        self.assertTrue(any("Problem" in item and "蓝色来源" in item for item in report.errors))

    def test_single_word_bold_is_too_fragmentary(self):
        wb = load_workbook(self.path, rich_text=True)
        ws = wb.active
        body = "The model uses a framework for planning decisions."
        ws["K2"] = review_text(body, "framework")
        wb.save(self.path)
        report = self.validate()
        self.assertTrue(any("Model" in item and "重点片段过短" in item for item in report.errors))

    def test_red_outside_innovation_fails(self):
        wb = load_workbook(self.path, rich_text=True)
        ws = wb.active
        body = "The central research gap concerns uncertain demand information."
        ws["H2"] = review_text(body, "uncertain demand information", red_override=True)
        wb.save(self.path)
        report = self.validate()
        self.assertTrue(any("Problem" in item and "红色" in item for item in report.errors))

    def test_innovation_requires_red_bold_focus(self):
        wb = load_workbook(self.path, rich_text=True)
        ws = wb.active
        body = "The innovation jointly models cargo acceptance and empty-container availability."
        ws["P2"] = review_text(
            body,
            "jointly models cargo acceptance and empty-container availability",
            innovation=False,
        )
        wb.save(self.path)
        report = self.validate()
        self.assertTrue(any("Innovation" in item and "红色加粗" in item for item in report.errors))

    def test_bare_acronym_without_full_name_fails(self):
        wb = load_workbook(self.path, rich_text=True)
        ws = wb.active
        body = "The MFD model represents regional traffic states and inter-region flows."
        ws["K2"] = review_text(body, "represents regional traffic states and inter-region flows")
        wb.save(self.path)
        report = self.validate()
        self.assertTrue(any("MFD" in item and "全称" in item for item in report.errors))


if __name__ == "__main__":
    unittest.main()
