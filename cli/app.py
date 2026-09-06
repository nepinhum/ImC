from __future__ import annotations

import argparse
from pathlib import Path

from cli.convert import ConvertOptions, convert_paths, parse_quality
from cli.utils import normalize_extension, readable_extensions, writable_extensions
from importlib.metadata import version, PackageNotFoundError


def parse_quality_arg(value: str) -> int:
    try:
        return parse_quality(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid quality: {exc}") from exc


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="converter",
        description="Convert images between formats using Pillow.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert_parser = subparsers.add_parser(
        "convert", help="Convert files or directories"
    )
    convert_parser.add_argument("input", nargs="+", help="File or directory path(s)")
    convert_parser.add_argument(
        "--to", "-t", required=True, help="Target extension (png, jpg, webp, ...)"
    )
    convert_parser.add_argument("--output", "-o", help="Output directory or file path")
    convert_parser.add_argument(
        "--recursive", "-r", action="store_true", help="Convert directories recursively"
    )
    convert_parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing files"
    )
    convert_parser.add_argument(
        "--remove-source",
        action="store_true",
        help="Remove source files after successful conversion",
    )
    convert_parser.add_argument(
        "--quality", type=parse_quality_arg, help="Quality for JPEG/WEBP/AVIF (1-100)"
    )

    subparsers.add_parser("list-formats", help="List supported extensions")

    subparsers.add_parser("version", help="Show version")

    return parser


def _handle_list_formats() -> int:
    readable = sorted(readable_extensions().keys())
    writable = sorted(writable_extensions().keys())
    print("Readable:")
    print(" ".join(readable))
    print("Writable:")
    print(" ".join(writable))
    return 0


def _output_is_file(inputs: list[Path], output: Path | None) -> bool:
    if output is None:
        return False
    if len(inputs) != 1 or inputs[0].is_dir():
        return False
    if output.exists():
        return output.is_file()
    return bool(output.suffix)


def _handle_convert(args: argparse.Namespace) -> int:
    target_extension = normalize_extension(args.to)
    output = Path(args.output).expanduser() if args.output else None
    quality = args.quality
    inputs = [Path(value).expanduser() for value in args.input]

    options = ConvertOptions(
        target_extension=target_extension,
        output=output,
        recursive=args.recursive,
        overwrite=args.overwrite,
        remove_source=args.remove_source,
        quality=quality,
        output_is_file=_output_is_file(inputs, output),
    )
    convert_paths(inputs, options)
    return 0


def get_version() -> str:
    try:
        return version("imc-image-converter")
    except PackageNotFoundError:
        return "0.0.0"


def _handle_version() -> int:
    print(get_version())
    return 0


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "list-formats":
        raise SystemExit(_handle_list_formats())
    if args.command == "convert":
        try:
            raise SystemExit(_handle_convert(args))
        except (ValueError, FileExistsError) as exc:
            parser.error(str(exc))
    if args.command == "version":
        raise SystemExit(_handle_version())
    raise SystemExit(1)
