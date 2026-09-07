"""Compose generated stickers in `stickers/` into print-ready sheets.

Reads PNGs from `stickers/` (skipping generated sheet files), arranges them
in filename order, and writes multiple output sheets of fixed physical size.

Default layout:
  - 12 inches wide x 8 inches tall
  - 300 DPI
  - 40 stickers per sheet
  - 8 columns x 5 rows

Each sticker is placed inside a padded, dotted cut-guide rectangle.

Usage:
    python pipeline/compile_sticker_sheet.py
    python pipeline/compile_sticker_sheet.py --dpi 300
    python pipeline/compile_sticker_sheet.py --per-sheet 40 --cols 8 --rows 5
    python pipeline/compile_sticker_sheet.py --sheet-width-in 12 --sheet-height-in 8

Requires: Pillow.
"""

import argparse
import sys
from math import ceil
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("error: Pillow not installed — pip install pillow", file=sys.stderr)
    sys.exit(1)


RESAMPLE_LANCZOS = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.LANCZOS)


STICKER_DIR = Path("stickers")
SKIP_NAMES = {"sheet.png", "oreoOS_gummy_sheet.png"}
DEFAULT_DPI = 300
DEFAULT_SHEET_WIDTH_IN = 12
DEFAULT_SHEET_HEIGHT_IN = 8
DEFAULT_COLS = 8
DEFAULT_ROWS = 5


def parse_args():
    p = argparse.ArgumentParser(
        description="Composite stickers/*.png into multiple print sheets."
    )
    p.add_argument("--sheet-width-in", type=float, default=DEFAULT_SHEET_WIDTH_IN,
                   help="sheet width in inches (default 12)")
    p.add_argument("--sheet-height-in", type=float, default=DEFAULT_SHEET_HEIGHT_IN,
                   help="sheet height in inches (default 8)")
    p.add_argument("--dpi", type=int, default=DEFAULT_DPI,
                   help="output DPI used to convert inches to pixels (default 300)")
    p.add_argument("--per-sheet", type=int, default=None,
                   help="stickers per output sheet; default = fill the grid")
    p.add_argument("--cols", type=int, default=DEFAULT_COLS,
                   help="stickers per row (default 8)")
    p.add_argument("--rows", type=int, default=None,
                   help="sticker rows per sheet; default 5, or enough for --per-sheet")
    p.add_argument("--gap", type=int, default=18,
                   help="gap between stickers in px (default 18)")
    p.add_argument("--margin", type=int, default=24,
                   help="outer page margin in px (default 24)")
    p.add_argument("--padding", type=int, default=18,
                   help="space between a sticker and its cut guide in px (default 18)")
    p.add_argument("--cut-line", default="#7A7065",
                   help="dotted cut-guide colour (default muted brown-grey)")
    p.add_argument("--bg", default="#FFF8EB",
                   help="sheet background colour (default warm ivory)")
    return p.parse_args()


def collect_stickers():
    """Every PNG in stickers/ except generated sheets. Sorted by name."""
    if not STICKER_DIR.is_dir():
        print(f"error: {STICKER_DIR}/ not found (run from repo root)",
              file=sys.stderr)
        sys.exit(1)

    files = sorted(
        p for p in STICKER_DIR.glob("*.png")
        if p.name not in SKIP_NAMES
        and not p.name.startswith(".")
        and not p.name.startswith("sheet_")
    )

    if not files:
        print(f"error: no PNGs found in {STICKER_DIR}/", file=sys.stderr)
        print("       generate them first, then re-run this script.",
              file=sys.stderr)
        sys.exit(1)

    return files


def dotted_rectangle(draw, box, fill, dot=4, space=6, width=1):
    """Draw a dotted rectangular cut guide, including its corners."""
    left, top, right, bottom = box
    step = dot + space

    for px in range(left, right + 1, step):
        draw.line((px, top, min(px + dot - 1, right), top), fill=fill, width=width)
        draw.line((px, bottom, min(px + dot - 1, right), bottom), fill=fill, width=width)
    for py in range(top, bottom + 1, step):
        draw.line((left, py, left, min(py + dot - 1, bottom)), fill=fill, width=width)
        draw.line((right, py, right, min(py + dot - 1, bottom)), fill=fill, width=width)


def make_sheet(files, out_path, sheet_w, sheet_h, cols, rows, cell_w, cell_h, gap, padding,
               bg, cut_line, dpi):
    sheet = Image.new("RGB", (sheet_w, sheet_h), bg)
    draw = ImageDraw.Draw(sheet)

    # Integer cell sizes can leave a few spare pixels. Centre the complete grid
    # so every output keeps the exact requested physical page dimensions.
    grid_w = cols * cell_w + (cols - 1) * gap
    grid_h = rows * cell_h + (rows - 1) * gap
    origin_x = (sheet_w - grid_w) // 2
    origin_y = (sheet_h - grid_h) // 2

    for i, fp in enumerate(files):
        r, c = divmod(i, cols)
        x = origin_x + c * (cell_w + gap)
        y = origin_y + r * (cell_h + gap)

        try:
            im = Image.open(fp).convert("RGBA")
        except Exception as e:
            print(f"  ! skipped {fp.name}: {e}")
            continue

        inner_w = max(1, cell_w - 2 * padding)
        inner_h = max(1, cell_h - 2 * padding)
        im.thumbnail((inner_w, inner_h), resample=RESAMPLE_LANCZOS)

        ox = x + (cell_w - im.width) // 2
        oy = y + (cell_h - im.height) // 2
        sheet.paste(im, (ox, oy), im)

        dotted_rectangle(draw, (x, y, x + cell_w - 1, y + cell_h - 1), cut_line)
        print(f"  + {fp.name} -> cell ({r}, {c})")

    sheet.save(out_path, format="PNG", optimize=True, compress_level=9,
               dpi=(dpi, dpi))
    return sheet_w, sheet_h


def main():
    args = parse_args()
    files = collect_stickers()

    cols = max(1, args.cols)
    if args.rows is not None:
        rows = max(1, args.rows)
    elif args.per_sheet is not None:
        rows = max(1, ceil(max(1, args.per_sheet) / cols))
    else:
        rows = DEFAULT_ROWS
    capacity = cols * rows
    per_sheet = capacity if args.per_sheet is None else max(1, args.per_sheet)

    sheet_w_px = max(1, round(args.sheet_width_in * args.dpi))
    sheet_h_px = max(1, round(args.sheet_height_in * args.dpi))

    usable_w = sheet_w_px - 2 * max(0, args.margin) - (cols - 1) * max(0, args.gap)
    usable_h = sheet_h_px - 2 * max(0, args.margin) - (rows - 1) * max(0, args.gap)

    if usable_w <= 0 or usable_h <= 0:
        print("error: margins/gaps leave no usable page area", file=sys.stderr)
        sys.exit(1)

    cell_w = usable_w // cols
    cell_h = usable_h // rows

    if cell_w < 1 or cell_h < 1:
        print("error: sheet too small for the requested grid", file=sys.stderr)
        sys.exit(1)

    if per_sheet > capacity:
        print(f"warning: --per-sheet {per_sheet} exceeds grid capacity {capacity}; "
              f"using {capacity} per sheet")
        per_sheet = capacity

    print(f"sheet size: {args.sheet_width_in}x{args.sheet_height_in} in @ {args.dpi} DPI "
          f"= {sheet_w_px}x{sheet_h_px}px")
    print(f"grid: {cols}x{rows} ({per_sheet} stickers per sheet) -> cell {cell_w}x{cell_h}px")

    batches = [files[i:i + per_sheet] for i in range(0, len(files), per_sheet)]

    for sheet_index, batch in enumerate(batches, start=1):
        out_path = STICKER_DIR / f"sheet_{sheet_index:02d}.png"
        print(f"compiling sheet {sheet_index:02d} with {len(batch)} stickers -> {out_path}")
        sheet_w, sheet_h = make_sheet(
            batch,
            out_path,
            sheet_w_px,
            sheet_h_px,
            cols,
            rows,
            cell_w,
            cell_h,
            max(0, args.gap),
            max(0, args.padding),
            args.bg,
            args.cut_line,
            args.dpi,
        )
        print(f"wrote {out_path} ({sheet_w}x{sheet_h}px)")

    expected_outputs = {STICKER_DIR / f"sheet_{i:02d}.png"
                        for i in range(1, len(batches) + 1)}
    for stale_path in sorted(STICKER_DIR.glob("sheet_*.png")):
        suffix = stale_path.stem.removeprefix("sheet_")
        if suffix.isdigit() and stale_path not in expected_outputs:
            stale_path.unlink()
            print(f"removed stale sheet {stale_path}")

    print(f"done: {len(files)} stickers split across {len(batches)} sheet(s)")


if __name__ == "__main__":
    main()
