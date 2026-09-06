# ImC Image Converter

Fast, simple image format conversion for files. Built on Pillow

## Features
- Convert between many formats (`png`, `jpg`, `webp` and more).
- Batch conversion for files and directories.
- Optional recursive traversal.
- Optional removal of source files after successful conversion.

## Setup
```bash
pip install -r requirements.txt
```

## Quick Start
```bash
python main.py list-formats
python main.py convert image.webp --to png
python main.py convert images/ --to jpg --recursive --output out
python main.py convert image.png --to webp --remove-source
```

## Commands
| Command | Description | Example |
| --- | --- | --- |
| `list-formats` | List all supported extensions. | `python main.py list-formats` |
| `convert` | Convert files or directories to a target format. | `python main.py convert images/ --to png` |

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

## Usage Examples
Convert a single file to PNG:
```bash
python main.py convert image.webp --to png
```

Convert a folder recursively and delete originals:
```bash
python main.py convert photos/ --to jpg --recursive --remove-source
```

Save outputs to a different directory:
```bash
python main.py convert photos/ --to webp --recursive --output converted/
```

Set quality for JPEG/WEBP/AVIF:
```bash
python main.py convert image.png --to jpg --quality 85
```
