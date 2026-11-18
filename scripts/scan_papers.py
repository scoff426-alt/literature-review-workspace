from __future__ import annotations

from common import INVENTORY_FIELDS, cards_path, inventory_path, parse_cards, pdfs, read_inventory, resolve_workspace, slug_from_pdf, workspace_arg, write_inventory


def main() -> None:
    parser = workspace_arg()
    args = parser.parse_args()
    workspace = resolve_workspace(args.workspace)
    inv_path = inventory_path(workspace)
    existing = read_inventory(inv_path)
    cards = parse_cards(cards_path(workspace))
    by_file = {row.get("PDF File", ""): row for row in existing if row.get("PDF File")}

    rows = []
    for idx, pdf in enumerate(pdfs(workspace), start=1):
        pdf_name = pdf.relative_to(workspace).as_posix()
        row = by_file.get(pdf_name, {})
        merged = {field: row.get(field, "") for field in INVENTORY_FIELDS}
        merged["Paper ID"] = merged["Paper ID"] or f"{idx:02d}"
        merged["Title"] = merged["Title"] or slug_from_pdf(pdf)
        merged["PDF File"] = pdf_name
        card = cards.get(merged["Paper ID"], {})
        for field in ["Authors / Year", "Venue", "中科院分区", "DOI", "Category", "Keywords"]:
            merged[field] = merged[field] or card.get(field, "")
        if not merged["Source URL"] and merged["DOI"].startswith("http"):
            merged["Source URL"] = merged["DOI"]
        merged["Status"] = merged["Status"] or "PDF found; metadata needs review"
        rows.append(merged)

    known_files = {row["PDF File"] for row in rows}
    for row in existing:
        if row.get("PDF File") and row["PDF File"] not in known_files:
            row["Status"] = "PDF missing"
            rows.append(row)

    write_inventory(inv_path, rows)
    print(f"Scanned {len(pdfs(workspace))} PDF files.")
    print(f"Updated inventory: {inv_path}")


if __name__ == "__main__":
    main()
