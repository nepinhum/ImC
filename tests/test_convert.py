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
    output_is_file: bool = False,
) -> ConvertOptions:
    return ConvertOptions(
        target_extension=target_extension,
        output=output,
        recursive=recursive,
        overwrite=overwrite,
        remove_source=remove_source,
        quality=quality,
        output_is_file=output_is_file,
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


def test_recursive_conversion_skips_existing_output_tree(tmp_path: Path):
    root = tmp_path / "photos"
    source = make_image(root / "a.png")
    existing_output = make_image(root / "converted" / "old.png")

    converted = convert_paths(
        [root],
        options(target_extension=".webp", output=root / "converted", recursive=True),
    )

    assert converted == [root / "converted" / "a.webp"]
    assert (root / "converted" / "a.webp").exists()
    assert existing_output.exists()
    assert not (root / "converted" / "converted" / "old.webp").exists()
    assert source.exists()


def test_explicit_non_image_file_is_not_converted(tmp_path: Path):
    source = tmp_path / "README.md"
    source.write_text("# not an image\n", encoding="utf-8")

    converted = convert_paths([source], options(target_extension=".png"))

    assert converted == []
    assert not (tmp_path / "README.png").exists()


def test_dotted_output_directory_is_allowed_for_folder_input(tmp_path: Path):
    source_dir = tmp_path / "photos"
    output_dir = tmp_path / "archive.images"
    make_image(source_dir / "a.webp")

    converted = convert_paths(
        [source_dir],
        options(target_extension=".png", output=output_dir, recursive=False),
    )

    assert converted == [output_dir / "a.png"]
    assert (output_dir / "a.png").exists()


def test_recursive_multiple_directories_preserve_root_names(tmp_path: Path):
    cats = tmp_path / "cats"
    dogs = tmp_path / "dogs"
    output = tmp_path / "out"
    make_image(cats / "x" / "a.png")
    make_image(dogs / "x" / "a.png")

    converted = convert_paths(
        [cats, dogs],
        options(target_extension=".jpg", output=output, recursive=True),
    )

    assert converted == [
        output / "cats" / "x" / "a.jpg",
        output / "dogs" / "x" / "a.jpg",
    ]
    assert (output / "cats" / "x" / "a.jpg").exists()
    assert (output / "dogs" / "x" / "a.jpg").exists()
