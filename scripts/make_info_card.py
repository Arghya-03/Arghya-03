from pathlib import Path
import os
import html


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

OUTPUT_FILE = ROOT / "info-card.svg"


# ============================================================
# CARD SETTINGS
# ============================================================

WIDTH = 490
HEIGHT = 330

BACKGROUND = "#0d1117"
BORDER = "#30363d"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
ACCENT = "#58a6ff"
GREEN = "#3fb950"


# ============================================================
# INFORMATION
# ============================================================

NAME = "Arghya Maji"
USERNAME = "Arghya-03"

ROLE = "Student & Developer"

LINES = [
    ("Name", "Arghya Maji"),
    ("Role", "Student & Developer"),
    ("Languages", "C • Java • Python • JavaScript"),
    ("Frontend", "HTML • CSS • JavaScript • React"),
    ("Backend", "Node.js • Express"),
    ("Database", "MySQL • MongoDB"),
    ("Interests", "Web Development • Full Stack"),
]


# ============================================================
# ANIMATION
# ============================================================

LINE_DELAY = 0.18


# ============================================================
# STATIC MODE
# ============================================================

STATIC = os.getenv("STATIC", "0") == "1"


# ============================================================
# SVG HELPERS
# ============================================================

def esc(value):
    return html.escape(value)


svg = []


# ============================================================
# SVG HEADER
# ============================================================

svg.append(
    f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}">

<rect
x="1"
y="1"
width="{WIDTH - 2}"
height="{HEIGHT - 2}"
rx="12"
fill="{BACKGROUND}"
stroke="{BORDER}"
stroke-width="2"/>

<style>

.card-title {{
    font-family:
        "Cascadia Mono",
        "Consolas",
        "Liberation Mono",
        monospace;

    font-size: 17px;

    font-weight: bold;

    fill: {ACCENT};
}}

.card-command {{
    font-family:
        "Cascadia Mono",
        "Consolas",
        "Liberation Mono",
        monospace;

    font-size: 13px;

    fill: {MUTED};
}}

.key {{
    font-family:
        "Cascadia Mono",
        "Consolas",
        "Liberation Mono",
        monospace;

    font-size: 13px;

    fill: {ACCENT};

    font-weight: bold;
}}

.value {{
    font-family:
        "Cascadia Mono",
        "Consolas",
        "Liberation Mono",
        monospace;

    font-size: 13px;

    fill: {TEXT};
}}

.status {{
    font-family:
        "Cascadia Mono",
        "Consolas",
        "Liberation Mono",
        monospace;

    font-size: 12px;

    fill: {GREEN};
}}

.line {{
    opacity: {1 if STATIC else 0};

    animation:
        fadeIn
        0.45s
        ease-out
        forwards;
}}

@keyframes fadeIn {{

    from {{
        opacity: 0;
        transform: translateX(-12px);
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
# TERMINAL HEADER
# ============================================================

svg.append(
    '''
<circle cx="22" cy="24" r="5" fill="#ff5f56"/>
<circle cx="40" cy="24" r="5" fill="#ffbd2e"/>
<circle cx="58" cy="24" r="5" fill="#27c93f"/>
'''
)


svg.append(
    f'''
<text
x="80"
y="29"
class="card-command">
arghya@github ~ $ whoami
</text>
'''
)


# ============================================================
# TITLE
# ============================================================

svg.append(
    f'''
<text
x="28"
y="65"
class="card-title">
{esc(NAME)}
</text>
'''
)


svg.append(
    '''
<line
x1="28"
y1="78"
x2="462"
y2="78"
stroke="#30363d"
stroke-width="1"/>
'''
)


# ============================================================
# INFORMATION ROWS
# ============================================================

START_Y = 108
ROW_HEIGHT = 30

for index, (key, value) in enumerate(LINES):

    y = START_Y + index * ROW_HEIGHT

    delay = index * LINE_DELAY

    if STATIC:
        animation_style = ""
    else:
        animation_style = (
            f"animation-delay:{delay:.2f}s;"
        )

    svg.append(
        f'''
<g
class="line"
style="{animation_style}">

<text
x="28"
y="{y}"
class="key">
{esc(key)}
</text>

<text
x="135"
y="{y}"
class="value">
{esc(value)}
</text>

</g>
'''
    )


# ============================================================
# STATUS
# ============================================================

status_y = START_Y + len(LINES) * ROW_HEIGHT + 8

svg.append(
    f'''
<text
x="28"
y="{status_y}"
class="status">

● currently building &amp; learning

</text>
'''
)


# ============================================================
# CLOSE SVG
# ============================================================

svg.append("</svg>")


# ============================================================
# WRITE FILE
# ============================================================

OUTPUT_FILE.write_text(
    "".join(svg),
    encoding="utf-8"
)


print("----------------------------------------")
print("INFO CARD CREATED")
print("----------------------------------------")
print(f"Output: {OUTPUT_FILE}")
print("----------------------------------------")