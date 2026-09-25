import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).parent


def generate_allure_report(raw_results_dir: str, report_dir: Path) -> None:
    allure_cmd = shutil.which("allure") or shutil.which("allure.bat") or shutil.which("allure.cmd")
    if not allure_cmd:
        print("[run.py] 找不到 Allure commandline，略過報告產生。", file=sys.stderr)
        return

    try:
        subprocess.run(
            [allure_cmd, "generate", raw_results_dir, "-o", str(report_dir), "--clean"],
            shell=(os.name == "nt"),
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"[run.py] Allure 報告產生失敗: {e}", file=sys.stderr)


def main() -> int:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    report_dir = ROOT_DIR / "report" / timestamp
    raw_results_dir = tempfile.mkdtemp(prefix="allure-results-")

    try:
        exit_code = pytest.main(sys.argv[1:] + ["--alluredir", raw_results_dir])
        generate_allure_report(raw_results_dir, report_dir)
    finally:
        shutil.rmtree(raw_results_dir, ignore_errors=True)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
