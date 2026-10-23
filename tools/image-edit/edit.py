#!/usr/bin/env python3
"""
image-edit — Western Heart image editing tool.

Two modes:
  1. BASIC (PIL, works offline, no credentials):
     resize, crop, rotate, flip, brightness, contrast, saturation,
     hue shift, tint, grayscale, blur, sharpen, overlay, text, convert.

  2. GENERATIVE (--instruction, natural-language edits):
     Routes to a pluggable backend. See backends.py for what's available
     and what each one needs (GPU, API token, or nothing).

Usage:
    python edit.py input.png --resize 800x600 -o out.png
    python edit.py input.png --instruction "make the shell red" --backend pollinations -o out.png
    python edit.py input_dir/ --batch --resize 512x512 --convert jpg -o out_dir/

Part of the Western Heart creation suite (tools/image-edit/).
MIT licensed.
"""
import argparse
import os
import sys

from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont, ImageOps
import colorsys


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_size(s):
    """'800x600' -> (800, 600)."""
    w, h = s.lower().split("x")
    return int(w), int(h)


def parse_box(s):
    """'x,y,w,h' or 'x1,y1,x2,y2' -> (left, upper, right, lower)."""
    parts = [int(p) for p in s.split(",")]
    if len(parts) != 4:
        raise ValueError(f"--crop needs 4 numbers, got: {s}")
    x, y, a, b = parts
    # Heuristic: if a,b look like width/height relative to x,y use them as such
    # when the resulting box would exceed a same-size assumption. We treat the
    # input as x,y,width,height (most intuitive for users).
    return (x, y, x + a, y + b)


def hex_to_rgb(s):
    s = s.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def get_font(size):
    """Best-effort font lookup."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Basic operations (PIL — always available)
# ---------------------------------------------------------------------------

def op_resize(img, size_str):
    w, h = parse_size(size_str)
    return img.resize((w, h), Image.LANCZOS)


def op_crop(img, box_str):
    return img.crop(parse_box(box_str))


def op_rotate(img, degrees, expand=True):
    return img.rotate(-float(degrees), expand=expand, resample=Image.BICUBIC)


def op_flip(img, direction):
    if direction == "horizontal":
        return ImageOps.mirror(img)
    elif direction == "vertical":
        return ImageOps.flip(img)
    raise ValueError(f"--flip must be horizontal|vertical, got: {direction}")


def op_brightness(img, factor):
    return ImageEnhance.Brightness(img).enhance(float(factor))


def op_contrast(img, factor):
    return ImageEnhance.Contrast(img).enhance(float(factor))


def op_saturation(img, factor):
    return ImageEnhance.Color(img).enhance(float(factor))


def op_sharpness(img, factor):
    return ImageEnhance.Sharpness(img).enhance(float(factor))


def op_hue(img, degrees):
    """Shift hue by N degrees (0-360)."""
    shift = (float(degrees) % 360) / 360.0
    img = img.convert("RGB")
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            hh, ss, vv = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            hh = (hh + shift) % 1.0
            nr, ng, nb = colorsys.hsv_to_rgb(hh, ss, vv)
            pixels[x, y] = (int(nr * 255), int(ng * 255), int(nb * 255))
    return img


def op_tint(img, color, strength=0.3):
    """Blend a solid color over the image."""
    color = hex_to_rgb(color)
    strength = float(strength)
    overlay = Image.new("RGB", img.size, color)
    base = img.convert("RGB")
    return Image.blend(base, overlay, max(0.0, min(1.0, strength)))


def op_grayscale(img):
    return ImageOps.grayscale(img).convert("RGB")


def op_blur(img, radius=2.0):
    return img.filter(ImageFilter.GaussianBlur(float(radius)))


def op_overlay(img, overlay_path, pos="bottom-right", opacity=1.0, scale=None):
    """Composite another image on top."""
    base = img.convert("RGBA")
    ov = Image.open(overlay_path).convert("RGBA")
    if scale:
        sw, sh = parse_size(scale)
        ov = ov.resize((sw, sh), Image.LANCZOS)
    opacity = float(opacity)
    if opacity < 1.0:
        alpha = ov.split()[3].point(lambda v: int(v * opacity))
        ov.putalpha(alpha)
    bw, bh = base.size
    ow, oh = ov.size
    positions = {
        "top-left": (0, 0),
        "top-center": ((bw - ow) // 2, 0),
        "top-right": (bw - ow, 0),
        "center": ((bw - ow) // 2, (bh - oh) // 2),
        "bottom-left": (0, bh - oh),
        "bottom-center": ((bw - ow) // 2, bh - oh),
        "bottom-right": (bw - ow, bh - oh),
    }
    if pos not in positions:
        # "x,y" pixel coordinates
        try:
            x, y = (int(p) for p in pos.split(","))
            xy = (x, y)
        except ValueError:
            raise ValueError(f"--overlay-pos must be one of {list(positions)} or x,y")
    else:
        xy = positions[pos]
    base.alpha_composite(ov, xy)
    return base.convert("RGB")


def op_text(img, text, pos="bottom-center", size=48, color="#ffffff",
            stroke=2, stroke_color="#000000", font_path=None):
    """Draw text on the image."""
    base = img.convert("RGB")
    draw = ImageDraw.Draw(base)
    font = ImageFont.truetype(font_path, int(size)) if font_path else get_font(int(size))
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=int(stroke))
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    bw, bh = base.size
    positions = {
        "top-left": (10, 10),
        "top-center": ((bw - tw) // 2, 10),
        "top-right": (bw - tw - 10, 10),
        "center": ((bw - tw) // 2, (bh - th) // 2),
        "bottom-left": (10, bh - th - 10),
        "bottom-center": ((bw - tw) // 2, bh - th - 10),
        "bottom-right": (bw - tw - 10, bh - th - 10),
    }
    xy = positions.get(pos, positions["bottom-center"])
    if pos not in positions:
        try:
            xy = tuple(int(p) for p in pos.split(","))
        except ValueError:
            pass
    draw.text(xy, text, font=font, fill=color,
              stroke_width=int(stroke), stroke_fill=stroke_color)
    return base


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

BASIC_OPS = [
    # (arg_name, handler, takes_value)
    ("resize", op_resize, True),
    ("crop", op_crop, True),
    ("rotate", op_rotate, True),
    ("flip", op_flip, True),
    ("brightness", op_brightness, True),
    ("contrast", op_contrast, True),
    ("saturation", op_saturation, True),
    ("sharpness", op_sharpness, True),
    ("hue", op_hue, True),
    ("grayscale", lambda img, v: op_grayscale(img), False),
]


def apply_basic_ops(img, args):
    """Apply PIL ops in a sensible order."""
    if args.resize:
        img = op_resize(img, args.resize)
    if args.crop:
        img = op_crop(img, args.crop)
    if args.rotate:
        img = op_rotate(img, args.rotate, expand=not args.no_expand)
    if args.flip:
        img = op_flip(img, args.flip)
    if args.grayscale:
        img = op_grayscale(img)
    if args.brightness:
        img = op_brightness(img, args.brightness)
    if args.contrast:
        img = op_contrast(img, args.contrast)
    if args.saturation:
        img = op_saturation(img, args.saturation)
    if args.sharpness:
        img = op_sharpness(img, args.sharpness)
    if args.hue:
        img = op_hue(img, args.hue)
    if args.tint:
        img = op_tint(img, args.tint, args.tint_strength)
    if args.blur:
        img = op_blur(img, args.blur)
    if args.overlay:
        img = op_overlay(img, args.overlay, args.overlay_pos,
                         args.overlay_opacity, args.overlay_scale)
    if args.text:
        img = op_text(img, args.text, args.text_pos, args.text_size,
                      args.text_color, args.text_stroke,
                      args.text_stroke_color, args.font)
    return img


def save_image(img, path, fmt=None, quality=92):
    fmt = fmt or os.path.splitext(path)[1].lstrip(".").lower() or "png"
    fmt_map = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "webp": "WEBP", "bmp": "BMP"}
    pil_fmt = fmt_map.get(fmt, fmt.upper())
    kwargs = {}
    if pil_fmt in ("JPEG", "WEBP"):
        kwargs["quality"] = int(quality)
    if pil_fmt == "JPEG" and img.mode in ("RGBA", "LA"):
        img = img.convert("RGB")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    img.save(path, pil_fmt, **kwargs)
    return path


def process_one(input_path, args, output_path):
    img = Image.open(input_path).convert("RGB")

    # Generative pass first (operates on the source image)
    if args.instruction:
        from backends import run_instruction
        img = run_instruction(img, args.instruction,
                              backend=args.backend,
                              size=args.gen_size,
                              seed=args.seed)

    # Basic PIL ops after
    img = apply_basic_ops(img, args)

    fmt = args.convert
    if not fmt and output_path:
        fmt = os.path.splitext(output_path)[1].lstrip(".").lower() or None
    save_image(img, output_path, fmt=fmt, quality=args.quality)
    print(f"wrote {output_path}")
    return output_path


def process_batch(input_dir, args, output_dir):
    exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
    files = [f for f in sorted(os.listdir(input_dir))
             if os.path.splitext(f)[1].lower() in exts]
    if not files:
        print(f"no images found in {input_dir}", file=sys.stderr)
        return
    os.makedirs(output_dir, exist_ok=True)
    for i, fname in enumerate(files):
        src = os.path.join(input_dir, fname)
        stem = os.path.splitext(fname)[0]
        ext = (args.convert or os.path.splitext(fname)[1].lstrip(".")).lower()
        dst = os.path.join(output_dir, f"{stem}.{ext}")
        print(f"[{i + 1}/{len(files)}] {fname} ...")
        try:
            process_one(src, args, dst)
        except Exception as e:
            print(f"  FAILED: {e}", file=sys.stderr)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(
        description="image-edit — Western Heart image editing tool (PIL + generative backends).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  %(prog)s in.png --resize 800x600 -o out.png
  %(prog)s in.png --crop 0,0,400,400 --rotate 90 --flip horizontal -o out.png
  %(prog)s in.png --brightness 1.2 --saturation 1.4 --tint "#ff8800" --tint-strength 0.25 -o out.png
  %(prog)s in.png --hue 180 -o out.png
  %(prog)s in.png --overlay logo.png --overlay-pos bottom-right --overlay-opacity 0.6 -o out.png
  %(prog)s in.png --text "DOROWANI" --text-pos top-center --text-size 64 -o out.png
  %(prog)s in.png --convert webp -o out.webp
  %(prog)s in_dir/ --batch --resize 512x512 --convert jpg -o out_dir/
  %(prog)s in.png --instruction "make the shell red and white" --backend pollinations -o out.png
  %(prog)s in.png --instruction "change the sky to sunset" --backend hf -o out.png   # needs HF_TOKEN
  %(prog)s in.png --instruction "make it cyberpunk" --backend local -o out.png       # needs GPU + diffusers
""")
    p.add_argument("input", help="input image file, or directory with --batch")
    p.add_argument("-o", "--output", help="output file (or directory with --batch)")
    p.add_argument("--batch", action="store_true", help="process every image in input directory")

    # Generative
    p.add_argument("--instruction", help="natural-language edit instruction (generative mode)")
    p.add_argument("--backend", default="auto",
                   choices=["auto", "pollinations", "hf", "local"],
                   help="generative backend (default: auto)")
    p.add_argument("--gen-size", type=int, default=512,
                   help="working size for generative backend (default: 512)")
    p.add_argument("--seed", type=int, default=None, help="random seed for generative backend")

    # Geometry
    p.add_argument("--resize", metavar="WxH", help="resize to WIDTHxHEIGHT, e.g. 800x600")
    p.add_argument("--crop", metavar="x,y,w,h", help="crop box as x,y,width,height")
    p.add_argument("--rotate", metavar="DEG", help="rotate clockwise by degrees")
    p.add_argument("--no-expand", action="store_true", help="don't expand canvas on rotate")
    p.add_argument("--flip", choices=["horizontal", "vertical"], help="mirror the image")

    # Color
    p.add_argument("--brightness", metavar="F", help="brightness factor (1.0 = unchanged)")
    p.add_argument("--contrast", metavar="F", help="contrast factor (1.0 = unchanged)")
    p.add_argument("--saturation", metavar="F", help="saturation factor (1.0 = unchanged, 0 = grayscale)")
    p.add_argument("--sharpness", metavar="F", help="sharpness factor (1.0 = unchanged)")
    p.add_argument("--hue", metavar="DEG", help="shift hue by degrees (0-360)")
    p.add_argument("--tint", metavar="COLOR", help="tint color as hex, e.g. #ff8800")
    p.add_argument("--tint-strength", default=0.3, metavar="F", help="tint blend 0-1 (default: 0.3)")
    p.add_argument("--grayscale", action="store_true", help="convert to grayscale")
    p.add_argument("--blur", metavar="R", help="gaussian blur radius")

    # Composite
    p.add_argument("--overlay", metavar="FILE", help="overlay image composited on top")
    p.add_argument("--overlay-pos", default="bottom-right",
                   help="top-left|top-center|top-right|center|bottom-left|bottom-center|bottom-right|x,y")
    p.add_argument("--overlay-opacity", default=1.0, help="overlay opacity 0-1")
    p.add_argument("--overlay-scale", metavar="WxH", help="scale overlay to WIDTHxHEIGHT")

    # Text
    p.add_argument("--text", metavar="STR", help="text to draw on the image")
    p.add_argument("--text-pos", default="bottom-center", help="text position (same options as overlay-pos)")
    p.add_argument("--text-size", default=48, help="font size in px")
    p.add_argument("--text-color", default="#ffffff", help="text color hex")
    p.add_argument("--text-stroke", default=2, help="text outline width px")
    p.add_argument("--text-stroke-color", default="#000000", help="text outline color hex")
    p.add_argument("--font", metavar="FILE", help="path to a .ttf font")

    # Output
    p.add_argument("--convert", metavar="FMT", help="output format: png|jpg|webp|bmp")
    p.add_argument("--quality", default=92, help="JPEG/WebP quality 1-100 (default: 92)")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)

    if args.batch:
        if not os.path.isdir(args.input):
            print(f"error: --batch needs a directory, got: {args.input}", file=sys.stderr)
            return 2
        if not args.output:
            print("error: --batch needs -o/--output directory", file=sys.stderr)
            return 2
        process_batch(args.input, args, args.output)
        return 0

    if not os.path.isfile(args.input):
        print(f"error: input not found: {args.input}", file=sys.stderr)
        return 2
    if not args.output:
        print("error: -o/--output is required (unless --batch)", file=sys.stderr)
        return 2

    # Make backends importable when run from the tools dir
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    process_one(args.input, args, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
