# ImC Image Converter

Fast, simple image format conversion for files. Built on Pillow

## Features
- Convert between many formats (`png`, `jpg`, `webp` and more).
- Batch conversion for files and directories.
- Optional recursive traversal.
- Optional removal of source files after successful conversion.

## Setup

For normal CLI usage:

```bash
pipx install .
imc --help
```

For local development:

```bash
python -m pip install -e ".[dev]"
python main.py --help
```

## Quick Start
```bash
imc list-formats
imc convert image.webp --to png
imc convert images/ --to jpg --recursive --output out
imc convert image.png --to webp --remove-source
```

## Commands
| Command | Description | Example |
| --- | --- | --- |
| `list-formats` | List readable and writable extensions. | `imc list-formats` |
| `convert` | Convert files or directories to a target format. | `imc convert images/ --to png` |

## Flags (convert)
| Flag | Alias | Type | Default | Description |
| --- | --- | --- | --- | --- |
| `--to` | `-t` | string | required | Target extension (e.g. `png`, `jpg`, `webp`). |
| `--output` | `-o` | path | none | Output directory or file path. |
| `--recursive` | `-r` | boolean | `false` | Traverse folders recursively. |
| `--overwrite` |  | boolean | `false` | Overwrite existing files. |
| `--remove-source` |  | boolean | `false` | Remove source files after successful conversion. |
| `--quality` |  | integer | none | Quality for JPEG/WEBP/AVIF (1-100). |

## Output Rules
- If `--output` is omitted, converted files are saved next to their sources.
- For multiple inputs or any folder input, `--output` is always treated as an output directory.
- For one explicit file input, an existing `--output` directory receives the converted file.
- For one explicit file input, a non-existing `--output` path with a suffix is treated as the output file path.
- Recursive folder conversion preserves paths relative to the input folder inside the output directory.
- When recursively converting multiple folder inputs to one output directory, each input folder name is preserved under the output directory.

## Usage Examples
Convert a single file to PNG:
```bash
imc convert image.webp --to png
```

Convert a folder recursively and delete originals:
```bash
imc convert photos/ --to jpg --recursive --remove-source
```

Save outputs to a different directory:
```bash
imc convert photos/ --to webp --recursive --output converted/
```

Set quality for JPEG/WEBP/AVIF:
```bash
imc convert image.png --to jpg --quality 85
```

## Notes
- Metadata such as EXIF, ICC profiles, orientation tags and DPI is not preserved.
- When converting transparent images to JPEG, transparency is discarded by converting the image to RGB.
