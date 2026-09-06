from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image

from cli.utils import (
    collect_images,
    format_for_extension,
    normalize_extension,
    prepare_image_for_format,
)


@dataclass(frozen=True)
class ConvertOptions:
    target_extension: str
    output: Path | None
    recursive: bool
    overwrite: bool
    remove_source: bool
    quality: int | None
    output_is_file: bool = False


@dataclass(frozen=True)
class Conversion:
    source: Path
    target: Path
    target_format: str


def _target_path(source: Path, base_dir: Path, options: ConvertOptions) -> Path:
    target_name = source.stem + options.target_extension
    if options.output is None:
        return source.with_name(target_name)
    if options.output_is_file:
        return options.output
    if options.recursive and base_dir.is_dir():
        relative = source.relative_to(base_dir)
        return options.output / relative.with_suffix(options.target_extension)
    return options.output / target_name


def _excluded_output_dirs(path: Path, options: ConvertOptions) -> list[Path]:
    if options.output is None or not options.recursive or not path.is_dir():
        return []
    if options.output_is_file:
        return []
    try:
        options.output.resolve().relative_to(path.resolve())
    except ValueError:
        return []
    return [options.output]


def _save_image(
    img: Image.Image, target: Path, target_format: str, quality: int | None
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    save_kwargs = {}
    if quality is not None and target_format.upper() in {"JPEG", "JPG", "WEBP", "AVIF"}:
        save_kwargs["quality"] = quality
    if target_format.upper() == "PNG":
        save_kwargs["optimize"] = True
    img.save(target, format=target_format, **save_kwargs)


def plan_conversions(
    paths: Iterable[Path], options: ConvertOptions
) -> list[Conversion]:
    conversions: list[Conversion] = []
    target_format = format_for_extension(options.target_extension)
    for path in paths:
        base_dir = path if path.is_dir() else path.parent
        for source in collect_images(
            path, options.recursive, _excluded_output_dirs(path, options)
        ):
            conversions.append(
                Conversion(
                    source=source,
                    target=_target_path(source, base_dir, options),
                    target_format=target_format,
                )
            )
    return conversions


def validate_conversions(
    conversions: list[Conversion], options: ConvertOptions
) -> None:
    seen_targets: dict[Path, Path] = {}
    for conversion in conversions:
        if conversion.source.resolve() == conversion.target.resolve():
            raise ValueError(
                f"Source and target are the same file: {conversion.source}"
            )

        resolved_target = conversion.target.resolve()
        existing_source = seen_targets.get(resolved_target)
        if existing_source is not None:
            raise ValueError(
                f"Multiple inputs target the same output: {conversion.target}"
            )
        seen_targets[resolved_target] = conversion.source

    for conversion in conversions:
        if conversion.target.exists() and not options.overwrite:
            raise FileExistsError(f"Target already exists: {conversion.target}")


def _convert_one(conversion: Conversion, options: ConvertOptions) -> Path:
    with Image.open(conversion.source) as img:
        prepared = prepare_image_for_format(img, conversion.target_format)
        _save_image(
            prepared, conversion.target, conversion.target_format, options.quality
        )

    if options.remove_source:
        conversion.source.unlink()

    return conversion.target


def convert_paths(paths: Iterable[Path], options: ConvertOptions) -> list[Path]:
    conversions = plan_conversions(paths, options)
    validate_conversions(conversions, options)
    return [_convert_one(conversion, options) for conversion in conversions]


def parse_quality(value: str | None) -> int | None:
    if value is None:
        return None
    quality = int(value)
    if quality < 1 or quality > 100:
        raise ValueError("Quality must be between 1 and 100")
    return quality
