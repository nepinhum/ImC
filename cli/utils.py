from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image


def normalize_extension(ext: str) -> str:
    ext = ext.strip().lower()
    if not ext:
        raise ValueError("Target extension cannot be empty")
    if not ext.startswith("."):
        ext = "." + ext
    return ext


def available_extensions() -> dict[str, str]:
    return {ext.lower(): fmt for ext, fmt in Image.registered_extensions().items()}


def format_for_extension(ext: str) -> str:
    extensions = available_extensions()
    if ext not in extensions:
        raise ValueError(f"Unsupported extension: {ext}")
    return extensions[ext]


def is_image_path(path: Path) -> bool:
    if not path.is_file():
        return False
    extensions = available_extensions()
    return path.suffix.lower() in extensions


def collect_images(root: Path, recursive: bool) -> Iterable[Path]:
    if root.is_file():
        return [root]
    if not root.is_dir():
        return []
    if recursive:
        return [p for p in root.rglob("*") if is_image_path(p)]
    return [p for p in root.iterdir() if is_image_path(p)]


def prepare_image_for_format(img: Image.Image, target_format: str) -> Image.Image:
    target_format = target_format.upper()
    if target_format in {"JPEG", "JPG"}:
        if img.mode in {"RGBA", "LA"}:
            return img.convert("RGB")
        if img.mode == "P":
            return img.convert("RGB")
    if target_format == "BMP" and img.mode == "P":
        return img.convert("RGB")
    return img
