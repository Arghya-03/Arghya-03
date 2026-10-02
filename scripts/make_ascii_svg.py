from pathlib import Path
from PIL import Image, ImageEnhance
import html


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = ROOT / "assets" / "source-prepped.png"
OUTPUT_FILE = ROOT / "arghya-ascii.svg"


# ============================================================
# ASCII SETTINGS
# ============================================================

# Bright -> dark
RAMP = " .:-=+*#%@"

CHAR_WIDTH = 120
CHAR_ASPECT = 0.48

FONT_SIZE = 8

TEXT_COLOR = "#d0d7de"
BACKGROUND_COLOR = "#0d1117"


# ============================================================
# ANIMATION
# ============================================================

ROW_DELAY = 0.035
ROW_DURATION = 0.45


# ============================================================
# LOAD IMAGE
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Could not find: {INPUT_FILE}"
    )

image = Image.open(INPUT_FILE).convert("L")

print("Loaded image:", image.size)


# ============================================================
# FIND THE SUBJECT
# ============================================================

# Since prep_photo.py placed the person on a white
# background, we can find the non-white area ourselves.

threshold = 235

mask = image.point(
    lambda pixel: 255 if pixel < threshold else 0
)

bbox = mask.getbbox()


if bbox:

    left, top, right, bottom = bbox

    print(
        f"Subject detected: "
        f"left={left}, top={top}, "
        f"right={right}, bottom={bottom}"
    )

    subject_width = right - left
    subject_height = bottom - top

    # Add a little space around the subject.
    margin_x = int(subject_width * 0.08)
    margin_top = int(subject_height * 0.04)

    left = max(0, left - margin_x)
    right = min(
        image.width,
        right + margin_x
    )

    top = max(0, top - margin_top)

    # IMPORTANT:
    # Keep only the upper portion of the detected subject.
    #
    # This prevents the shirt/body from dominating
    # the ASCII portrait.

    bottom = min(
        image.height,
        top + int(subject_height * 0.82)
    )

    image = image.crop(
        (left, top, right, bottom)
    )

else:

    print(
        "WARNING: Subject could not be detected."
    )

    print(
        "Using the complete image."
    )


# ============================================================
# CONTRAST
# ============================================================

image = ImageEnhance.Contrast(
    image
).enhance(1.45)

image = ImageEnhance.Sharpness(
    image
).enhance(1.5)


# ============================================================
# RESIZE TO ASCII GRID
# ============================================================

original_width, original_height = image.size

char_height = max(
    1,
    int(
        CHAR_WIDTH
        * original_height
        / original_width
        * CHAR_ASPECT
    )
)

image = image.resize(
    (CHAR_WIDTH, char_height),
    Image.Resampling.LANCZOS
)

print(
    f"ASCII grid: "
    f"{CHAR_WIDTH} x {char_height}"
)


# ============================================================
# PIXELS -> ASCII
# ============================================================

pixels = list(image.getdata())

rows = []

for y in range(char_height):

    row = []

    for x in range(CHAR_WIDTH):

        brightness = pixels[
            y * CHAR_WIDTH + x
        ]

        # Dark pixel = dense character
        # Bright pixel = sparse character

        index = int(
            (255 - brightness)
            / 255
            * (len(RAMP) - 1)
        )

        index = max(
            0,
            min(index, len(RAMP) - 1)
        )

        row.append(
            RAMP[index]
        )

    rows.append(
        "".join(row)
    )


# ============================================================
# SVG DIMENSIONS
# ============================================================

line_height = FONT_SIZE * 1.35

svg_width = (
    CHAR_WIDTH
    * FONT_SIZE
    * 0.62
)

svg_height = (
    char_height * line_height
    + 20
)


# ============================================================
# CREATE SVG
# ============================================================

svg = []

svg.append(
    f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{svg_width:.0f}"
height="{svg_height:.0f}"
viewBox="0 0 {svg_width:.0f} {svg_height:.0f}">

<rect
width="100%"
height="100%"
fill="{BACKGROUND_COLOR}"/>

<style>

.ascii-row {{
    font-family:
        "Cascadia Mono",
        "Consolas",
        "Liberation Mono",
        monospace;

    font-size: {FONT_SIZE}px;

    fill: {TEXT_COLOR};

    white-space: pre;

    opacity: 0;

    animation:
        typeRow
        {ROW_DURATION}s
        ease-out
        forwards;
}}

@keyframes typeRow {{

    from {{
        opacity: 0;
        transform: translateX(-8px);
    }}

    to {{
        opacity: 1;
        transform: translateX(0);
    }}

}}

</style>
'''
)


# ============================================================
# ADD ASCII ROWS
# ============================================================

for row_index, row in enumerate(rows):

    y = (
        14
        + row_index * line_height
    )

    delay = (
        row_index * ROW_DELAY
    )

    svg.append(
        f'''
<text
x="8"
y="{y:.2f}"
class="ascii-row"
style="animation-delay:{delay:.3f}s">
{html.escape(row)}
</text>
'''
    )


# ============================================================
# CLOSE SVG
# ============================================================

svg.append("</svg>")


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.write_text(
    "".join(svg),
    encoding="utf-8"
)


print()
print("----------------------------------------")
print("ASCII SVG CREATED")
print("----------------------------------------")
print(f"Output: {OUTPUT_FILE}")
print("----------------------------------------")