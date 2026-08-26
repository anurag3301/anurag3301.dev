"""
Generates OpenGraph/Twitter-card banner images on the fly, with the post
title rendered onto a branded background. Used so links shared on
LinkedIn/Discord/etc. show a rich preview card for each blog post.

Images are cached on disk (keyed by a hash of the render inputs) so repeat
crawler hits don't re-render every time.
"""
import hashlib
import os
import textwrap
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_BOLD = os.path.join(BASE_DIR, "fonts", "Hack-Bold.ttf")
FONT_REGULAR = os.path.join(BASE_DIR, "fonts", "Hack-Regular.ttf")
CACHE_DIR = os.path.join(BASE_DIR, "og_cache")

WIDTH, HEIGHT = 1200, 630
BACKGROUND = (31, 34, 42)       # #1F222A - matches blog's dark theme
ACCENT = (120, 226, 160)        # matches blog's accent green
WHITE = (245, 245, 245)
MUTED = (150, 158, 170)

MAX_TITLE_FONT = 64
MIN_TITLE_FONT = 34
MARGIN_X = 90
CONTENT_TOP = 170
CONTENT_BOTTOM = 520

# Bump this whenever generate()'s drawing logic changes, so previously
# cached PNGs (keyed below) don't keep getting served after a code update.
TEMPLATE_VERSION = 2


def _wrap_to_fit(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _fit_title(draw, title, max_width, max_height):
    """Pick the largest font size (within bounds) whose wrapped title fits."""
    for size in range(MAX_TITLE_FONT, MIN_TITLE_FONT - 1, -2):
        font = ImageFont.truetype(FONT_BOLD, size)
        lines = _wrap_to_fit(draw, title, font, max_width)
        line_height = int(size * 1.35)
        total_height = line_height * len(lines)
        if total_height <= max_height and len(lines) <= 5:
            return font, lines, line_height
    # fall back to smallest size, truncate lines if needed
    font = ImageFont.truetype(FONT_BOLD, MIN_TITLE_FONT)
    lines = _wrap_to_fit(draw, title, font, max_width)
    line_height = int(MIN_TITLE_FONT * 1.35)
    max_lines = max_height // line_height
    if len(lines) > max_lines:
        lines = lines[: max_lines - 1] + [lines[max_lines - 1].rstrip() + " …"] if max_lines > 0 else lines[:1]
    return font, lines, line_height


def generate(title: str, site_label: str = "anurag3301", section_label: str = "blog") -> bytes:
    title = (title or "").strip() or "Untitled post"

    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_key = hashlib.sha256(
        f"v{TEMPLATE_VERSION}|{title}|{site_label}|{section_label}".encode()
    ).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"{cache_key}.png")
    if os.path.isfile(cache_path):
        with open(cache_path, "rb") as f:
            return f.read()

    img = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(img)

    # Accent bar on the left edge
    draw.rectangle([0, 0, 10, HEIGHT], fill=ACCENT)

    # Top logo row: "anurag3301" in accent, "/blog" in muted
    logo_font = ImageFont.truetype(FONT_BOLD, 34)
    label_font = ImageFont.truetype(FONT_REGULAR, 34)
    logo_x = MARGIN_X
    logo_y = 70
    draw.text((logo_x, logo_y), site_label, font=logo_font, fill=ACCENT)
    logo_w = draw.textlength(site_label, font=logo_font)
    draw.text((logo_x + logo_w, logo_y), f"/{section_label}", font=label_font, fill=MUTED)

    # Small caret marker above the title, terminal aesthetic
    caret_font = ImageFont.truetype(FONT_BOLD, 30)
    draw.text((MARGIN_X, 140), ">", font=caret_font, fill=ACCENT)

    # Title, auto-sized + wrapped to fit
    max_width = WIDTH - (MARGIN_X * 2)
    max_height = CONTENT_BOTTOM - CONTENT_TOP
    font, lines, line_height = _fit_title(draw, title, max_width, max_height)

    total_text_height = line_height * len(lines)
    start_y = CONTENT_TOP + max(0, (max_height - total_text_height) // 2)
    y = start_y
    for line in lines:
        draw.text((MARGIN_X, y), line, font=font, fill=WHITE)
        y += line_height

    # Footer: domain
    footer_font = ImageFont.truetype(FONT_REGULAR, 26)
    footer_text = f"{site_label}.dev/{section_label}"
    draw.text((MARGIN_X, HEIGHT - 80), footer_text, font=footer_font, fill=MUTED)

    buf = BytesIO()
    img.save(buf, format="PNG")
    data = buf.getvalue()

    try:
        with open(cache_path, "wb") as f:
            f.write(data)
    except OSError:
        pass  # caching is best-effort

    return data
