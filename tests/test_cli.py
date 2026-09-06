import subprocess
import sys
from pathlib import Path


def run_cli(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "main.py", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_invalid_quality_reports_argparse_error(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]

    result = run_cli(
        ["convert", "missing.png", "--to", "jpg", "--quality", "potato"], repo
    )

    assert result.returncode != 0
    assert "invalid quality" in result.stderr.lower()
    assert "Traceback" not in result.stderr


def test_unsupported_target_reports_cli_error(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]

    result = run_cli(["convert", "missing.png", "--to", "definitely-not-real"], repo)

    assert result.returncode != 0
    assert "unsupported extension" in result.stderr.lower()
    assert "Traceback" not in result.stderr
