import subprocess
import sys
from pathlib import Path

from PIL import Image


def run_cli(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "main.py", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def make_image(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (2, 2), (255, 0, 0))
    image.save(path)
    return path


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


def test_dotted_output_directory_is_allowed_for_folder_cli(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]
    source_dir = tmp_path / "photos"
    output_dir = tmp_path / "archive.images"
    make_image(source_dir / "a.webp")

    result = run_cli(
        ["convert", str(source_dir), "--to", "png", "--output", str(output_dir)],
        repo,
    )

    assert result.returncode == 0
    assert (output_dir / "a.png").exists()
