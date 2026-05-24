"""
Color extraction from clothing images.

Uses ColorThief for palette extraction, then maps raw hex values
to human-readable color names using the nearest-neighbor approach
in HSL space.
"""

from colorthief import ColorThief
from PIL import Image
import io
import math


# Named color reference palette (HSL-approximate)
NAMED_COLORS = [
    ("white",   (0,   0,   97)),
    ("black",   (0,   0,   5)),
    ("gray",    (0,   0,   50)),
    ("cream",   (45,  40,  90)),
    ("beige",   (30,  30,  75)),
    ("navy",    (220, 70,  20)),
    ("blue",    (210, 75,  50)),
    ("sky blue",(200, 65,  70)),
    ("red",     (0,   75,  50)),
    ("burgundy",(340, 60,  30)),
    ("pink",    (340, 60,  80)),
    ("hot pink",(330, 80,  60)),
    ("green",   (120, 60,  40)),
    ("olive",   (60,  40,  35)),
    ("sage",    (100, 25,  60)),
    ("yellow",  (55,  80,  60)),
    ("mustard", (45,  65,  45)),
    ("orange",  (25,  80,  55)),
    ("brown",   (25,  40,  30)),
    ("camel",   (35,  45,  55)),
    ("tan",     (30,  35,  65)),
    ("purple",  (270, 60,  45)),
    ("lavender",(260, 40,  75)),
    ("teal",    (175, 55,  40)),
    ("coral",   (15,  70,  65)),
    ("rust",    (15,  65,  45)),
    ("charcoal",(0,   0,   25)),
    ("ivory",   (45,  30,  95)),
    ("gold",    (45,  70,  50)),
    ("silver",  (0,   0,   75)),
]


def _rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    r_, g_, b_ = r / 255, g / 255, b / 255
    cmax = max(r_, g_, b_)
    cmin = min(r_, g_, b_)
    delta = cmax - cmin

    # Lightness
    l = (cmax + cmin) / 2

    # Saturation
    s = 0.0 if delta == 0 else delta / (1 - abs(2 * l - 1))

    # Hue
    if delta == 0:
        h = 0.0
    elif cmax == r_:
        h = 60 * (((g_ - b_) / delta) % 6)
    elif cmax == g_:
        h = 60 * (((b_ - r_) / delta) + 2)
    else:
        h = 60 * (((r_ - g_) / delta) + 4)

    return h, s * 100, l * 100


def _hsl_distance(a: tuple, b: tuple) -> float:
    dh = min(abs(a[0] - b[0]), 360 - abs(a[0] - b[0])) / 180
    ds = (a[1] - b[1]) / 100
    dl = (a[2] - b[2]) / 100
    return math.sqrt(dh**2 + ds**2 + dl**2)


def _nearest_color_name(r: int, g: int, b: int) -> str:
    hsl = _rgb_to_hsl(r, g, b)
    best_name, best_dist = "unknown", float("inf")
    for name, ref_hsl in NAMED_COLORS:
        d = _hsl_distance(hsl, ref_hsl)
        if d < best_dist:
            best_dist = d
            best_name = name
    return best_name


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02X}{g:02X}{b:02X}"


def extract_colors(image_path: str, num_colors: int = 5) -> list[dict]:
    """
    Extract dominant colors from a clothing image.

    Returns a list like:
        [{"hex": "#1A2B3C", "name": "navy", "pct": 0.62}, …]
    """
    ct = ColorThief(image_path)
    palette = ct.get_palette(color_count=num_colors, quality=5)

    # Estimate rough percentage by clustering distance (simple approximation)
    total = len(palette)
    results = []
    for i, (r, g, b) in enumerate(palette):
        pct = round((1 / total) * 100, 1)   # uniform approximation
        results.append({
            "hex": _rgb_to_hex(r, g, b),
            "name": _nearest_color_name(r, g, b),
            "pct": pct,
        })

    # Normalize so percentages sum to 100
    s = sum(c["pct"] for c in results)
    for c in results:
        c["pct"] = round(c["pct"] / s * 100, 1)

    return results
