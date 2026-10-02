from pathlib import Path
from datetime import date
import json
import html


# ============================================================
# SETTINGS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = ROOT / "data" / "contributions.json"
OUTPUT_FILE = ROOT / "contributions.svg"

WIDTH = 900
HEIGHT = 220

CELL_SIZE = 11
CELL_GAP = 3

LEFT = 55
TOP = 55


# ============================================================
# LOAD CONTRIBUTION DATA
# ============================================================

data = json.loads(
    DATA_FILE.read_text(
        encoding="utf-8"
    )
)

days = data["days"]

count_by_date = {
    item["date"]: item["count"]
    for item in days
}


# ============================================================
# CONTRIBUTION LEVEL
# ============================================================

def get_level(count):
    if count == 0:
        return 0
    elif count <= 2:
        return 1
    elif count <= 5:
        return 2
    elif count <= 10:
        return 3
    else:
        return 4


# ============================================================
# COLORS
# ============================================================

BACKGROUND = "#0d1117"
TEXT = "#8b949e"
BRIGHT_TEXT = "#c9d1d9"

LEVEL_COLORS = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
}


# ============================================================
# CREATE LAST 52 WEEKS
# ============================================================

today = date.today()

# Find the Sunday at the beginning of the current week.
week_start = today

while week_start.weekday() != 6:
    from datetime import timedelta
    week_start -= timedelta(days=1)


# Move back 51 weeks.
from datetime import timedelta

start_date = (
    week_start
    - timedelta(weeks=51)
)


# ============================================================
# SVG HEADER
# ============================================================

svg = []

svg.append(
    f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}">'''
)

svg.append(
    f'''
<style>
    .bg {{
        fill: {BACKGROUND};
    }}

    .text {{
        fill: {TEXT};
        font-family:
            "SFMono-Regular",
            Consolas,
            "Liberation Mono",
            monospace;
        font-size: 12px;
    }}

    .title {{
        fill: {BRIGHT_TEXT};
        font-family:
            "SFMono-Regular",
            Consolas,
            "Liberation Mono",
            monospace;
        font-size: 16px;
        font-weight: bold;
    }}

    .cell {{
        rx: 2;
        ry: 2;
    }}
</style>
'''
)

svg.append(
    f'<rect class="bg" width="{WIDTH}" height="{HEIGHT}" rx="10"/>'
)

svg.append(
    '<text x="25" y="28" class="title">'
    'contributions.log'
    '</text>'
)


# ============================================================
# MONTH LABELS
# ============================================================

current_month = None

for week in range(52):

    current_date = (
        start_date
        + timedelta(weeks=week)
    )

    month_name = current_date.strftime("%b")

    if month_name != current_month:

        x = (
            LEFT
            + week
            * (CELL_SIZE + CELL_GAP)
        )

        svg.append(
            f'<text x="{x}" y="47" class="text">'
            f'{html.escape(month_name)}'
            '</text>'
        )

        current_month = month_name


# ============================================================
# DAY LABELS
# ============================================================

day_labels = [
    (1, "Mon"),
    (3, "Wed"),
    (5, "Fri"),
]

for row, label in day_labels:

    y = (
        TOP
        + row
        * (CELL_SIZE + CELL_GAP)
        + 10
    )

    svg.append(
        f'<text x="15" y="{y}" class="text">'
        f'{label}'
        '</text>'
    )


# ============================================================
# CONTRIBUTION CELLS
# ============================================================

for week in range(52):

    for day_index in range(7):

        current_date = (
            start_date
            + timedelta(weeks=week)
            + timedelta(days=day_index)
        )

        date_string = (
            current_date.isoformat()
        )

        count = count_by_date.get(
            date_string,
            0
        )

        level = get_level(count)

        x = (
            LEFT
            + week
            * (CELL_SIZE + CELL_GAP)
        )

        y = (
            TOP
            + day_index
            * (CELL_SIZE + CELL_GAP)
        )

        svg.append(
            f'<rect '
            f'x="{x}" '
            f'y="{y}" '
            f'width="{CELL_SIZE}" '
            f'height="{CELL_SIZE}" '
            f'class="cell" '
            f'fill="{LEVEL_COLORS[level]}">'
            f'<title>'
            f'{date_string}: '
            f'{count} contribution'
            f'{"s" if count != 1 else ""}'
            f'</title>'
            f'</rect>'
        )


# ============================================================
# LEGEND
# ============================================================

legend_y = 185

svg.append(
    '<text x="600" y="189" class="text">'
    'Less'
    '</text>'
)

for level in range(5):

    x = (
        635
        + level
        * (CELL_SIZE + CELL_GAP)
    )

    svg.append(
        f'<rect '
        f'x="{x}" '
        f'y="{legend_y - 10}" '
        f'width="{CELL_SIZE}" '
        f'height="{CELL_SIZE}" '
        f'class="cell" '
        f'fill="{LEVEL_COLORS[level]}"/>'
    )

svg.append(
    '<text x="705" y="189" class="text">'
    'More'
    '</text>'
)


# ============================================================
# CLOSE SVG
# ============================================================

svg.append("</svg>")


OUTPUT_FILE.write_text(
    "\n".join(svg),
    encoding="utf-8"
)


# ============================================================
# RESULT
# ============================================================

print()
print("----------------------------------------")
print("CONTRIBUTION SVG CREATED")
print("----------------------------------------")
print(f"Input  : {DATA_FILE}")
print(f"Output : {OUTPUT_FILE}")
print("----------------------------------------")