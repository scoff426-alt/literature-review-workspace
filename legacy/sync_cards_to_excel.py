from __future__ import annotations

from common import cards_path, parse_cards, resolve_workspace, workbook_path, workspace_arg


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


def main() -> None:
    try:
        from openpyxl import load_workbook
        from openpyxl.styles import Font
    except ImportError as exc:
        raise SystemExit("openpyxl is required to sync cards to Excel.") from exc

    parser = workspace_arg()
    args = parser.parse_args()
    workspace = resolve_workspace(args.workspace)
    cards = parse_cards(cards_path(workspace))
    xlsx = workbook_path(workspace)
    if not xlsx.exists():
        raise SystemExit(f"Workbook not found: {xlsx}")

    wb = load_workbook(xlsx)
    ws = wb["Literature Review"] if "Literature Review" in wb.sheetnames else wb.active
    headers = {cell.value: idx + 1 for idx, cell in enumerate(ws[1])}
    updated = 0
    for row_idx in range(2, ws.max_row + 1):
        pid = str(ws.cell(row_idx, headers["Paper ID"]).value or "").strip()
        row_type = str(ws.cell(row_idx, headers["Row Type"]).value or "").strip()
        if row_type != "Summary" or pid not in cards:
            continue
        for target_field, aliases in SUMMARY_FIELD_ALIASES.items():
            if target_field not in headers:
                continue
            value = first_card_value(cards[pid], aliases)
            if value:
                cell = ws.cell(row_idx, headers[target_field])
                cell.value = value
                if target_field in {"Model", "Results", "Innovation", "Limitations", "Review Use"}:
                    cell.font = Font(bold=True)
        updated += 1

    wb.save(xlsx)
    print(f"Updated {updated} Summary rows from {cards_path(workspace)}")


def first_card_value(card: dict[str, str], aliases: tuple[str, ...]) -> str:
    for alias in aliases:
        value = card.get(alias, "")
        if value:
            return value
    return ""


if __name__ == "__main__":
    main()
