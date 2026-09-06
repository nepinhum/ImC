from pathlib import Path

import pytest
from PIL import Image

from cli.convert import ConvertOptions, convert_paths


def make_image(path: Path, mode: str = "RGB") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if mode == "RGBA":
        image = Image.new(mode, (2, 2), (255, 0, 0, 128))
    else:
        image = Image.new(mode, (2, 2), (255, 0, 0))
    image.save(path)
    return path


def options(
    *,
    target_extension: str = ".png",
    output: Path | None = None,
    recursive: bool = False,
    overwrite: bool = False,
    remove_source: bool = False,
    quality: int | None = None,
) -> ConvertOptions:
    return ConvertOptions(
        target_extension=target_extension,
        output=output,
        recursive=recursive,
        overwrite=overwrite,
        remove_source=remove_source,
        quality=quality,
    )


def test_single_file_converts_next_to_source(tmp_path: Path):
    source = make_image(tmp_path / "image.webp")

    converted = convert_paths([source], options(target_extension=".png"))

    assert converted == [tmp_path / "image.png"]
    assert (tmp_path / "image.png").is_file()
    assert source.is_file()
