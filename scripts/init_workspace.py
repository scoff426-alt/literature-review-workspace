from __future__ import annotations

from pathlib import Path

from common import CARDS_NAME, INVENTORY_NAME, cards_path, ensure_workspace_dirs, inventory_path, resolve_workspace, workspace_arg


def main() -> None:
    parser = workspace_arg()
    args = parser.parse_args()
    workspace = resolve_workspace(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    ensure_workspace_dirs(workspace)

    template_dir = Path(__file__).resolve().parents[1] / "templates"

    inv = inventory_path(workspace)
    if not inv.exists():
        inv.write_text((template_dir / "source_inventory.template.csv").read_text(encoding="utf-8"), encoding="utf-8-sig")

    cards = cards_path(workspace)
    if not cards.exists():
        cards.write_text((template_dir / "knowledge-card.template.md").read_text(encoding="utf-8"), encoding="utf-8")

    print(f"Initialized literature review workspace: {workspace}")
    print(f"- {INVENTORY_NAME}")
    print(f"- {CARDS_NAME}")
    print("- papers/")
    print("- outputs/")


if __name__ == "__main__":
    main()
