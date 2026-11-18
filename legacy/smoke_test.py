from __future__ import annotations

import subprocess
import sys
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def main() -> None:
    tmp_root = ROOT / ".tmp"
    workspace = tmp_root / "smoke_workspace"
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True)
    try:
        run("init_workspace.py", workspace)
        papers = workspace / "papers"
        papers.mkdir(exist_ok=True)
        (papers / "01_test_paper.pdf").write_text("%PDF-1.4 test\n", encoding="ascii")

        run("scan_papers.py", workspace)
        run("build_review_workbook.py", workspace)
        run("validate_workspace.py", workspace)

        final_result = run("validate_workspace.py", workspace, "--final", check=False)
        if final_result.returncode == 0:
            raise SystemExit("Expected --final validation to fail for a draft workbook without evidence screenshots.")

        run("normalize_evidence_images.py", workspace)
        normalized = workspace / "outputs" / "文献综述_evidence_normalized.xlsx"
        if not normalized.exists():
            raise SystemExit(f"Missing normalized workbook: {normalized}")

        print("Smoke test passed.")
    finally:
        if workspace.exists():
            shutil.rmtree(workspace, ignore_errors=True)


def run(script: str, workspace: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPTS / script), str(workspace), *args]
    result = subprocess.run(command, text=True, capture_output=True)
    if check and result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise SystemExit(result.returncode)
    return result


if __name__ == "__main__":
    main()
