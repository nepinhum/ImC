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


def test_existing_target_preflight_does_not_partially_convert(tmp_path: Path):
    first = make_image(tmp_path / "first.webp")
    second = make_image(tmp_path / "second.webp")
    make_image(tmp_path / "second.png")

    with pytest.raises(FileExistsError, match="Target already exists"):
        convert_paths([first, second], options(target_extension=".png"))

    assert not (tmp_path / "first.png").exists()
    assert first.exists()
    assert second.exists()


def test_remove_source_never_deletes_same_target_path(tmp_path: Path):
    source = make_image(tmp_path / "image.png")

    with pytest.raises(ValueError, match="Source and target are the same file"):
        convert_paths(
            [source],
            options(target_extension=".png", overwrite=True, remove_source=True),
        )

    assert source.exists()


def test_duplicate_targets_are_rejected_before_conversion(tmp_path: Path):
    jpg = make_image(tmp_path / "photo.jpg")
    png = make_image(tmp_path / "photo.png")

    with pytest.raises(ValueError, match="Multiple inputs target the same output"):
        convert_paths([jpg, png], options(target_extension=".webp", overwrite=True))

    assert not (tmp_path / "photo.webp").exists()
