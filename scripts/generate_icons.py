"""Utility to generate Mini Email CRM icon assets from a high-resolution PNG.

Usage:
    python scripts/generate_icons.py \
        --source resources/icons/app_icon_source.png \
        --output-dir resources/icons

The script will create per-size PNG variants (e.g. app_icon_64x64.png)
plus a multi-resolution ICO file (app_icon.ico).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

# PNG variants we want to emit alongside the ICO bundle.
PNG_SIZES = [16, 24, 32, 48, 64, 128, 256, 512]
ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]
BASE_NAME = "app_icon"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate icon assets from a high-res PNG")
    parser.add_argument(
        "--source",
        default="resources/icons/app_icon_source.png",
        help="Path to the high-resolution square PNG to resize (default: %(default)s)",
    )
    parser.add_argument(
        "--output-dir",
        default="resources/icons",
        help="Directory where resized icons will be written (default: %(default)s)",
    )
    return parser.parse_args()


def load_source_image(path: Path) -> Image.Image:
    if not path.exists():
        raise FileNotFoundError(
            f"Source image not found at {path}. Provide a square PNG (e.g. 1024x1024)."
        )

    try:
        image = Image.open(path)
        image.load()  # Force Pillow to read the file eagerly to catch errors early.
    except Exception as exc:  # noqa: BLE001
        raise ValueError(
            f"Failed to open '{path}'. Ensure it is a valid PNG image."
        ) from exc

    if image.width != image.height:
        raise ValueError(
            f"Source image must be square. Got {image.width}x{image.height}."
        )

    return image.convert("RGBA")


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def generate_png_variants(base_image: Image.Image, output_dir: Path) -> None:
    for size in PNG_SIZES:
        resized = base_image.resize((size, size), Image.Resampling.LANCZOS)
        target = output_dir / f"{BASE_NAME}_{size}x{size}.png"
        resized.save(target, format="PNG")
        print(f"✔ Saved {target}")


def generate_ico(base_image: Image.Image, output_dir: Path) -> None:
    ico_path = output_dir / f"{BASE_NAME}.ico"
    base_image.save(ico_path, format="ICO", sizes=[(s, s) for s in ICO_SIZES])
    print(f"✔ Saved {ico_path}")


def main() -> int:
    args = parse_args()
    source_path = Path(args.source)
    output_dir = Path(args.output_dir)

    try:
        source_image = load_source_image(source_path)
    except Exception as exc:  # noqa: BLE001
        print(exc, file=sys.stderr)
        return 1

    ensure_output_dir(output_dir)
    generate_png_variants(source_image, output_dir)
    generate_ico(source_image, output_dir)
    print("Icon generation complete.✅")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
