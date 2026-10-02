from pathlib import Path
from datetime import date, timedelta
import json
import re

import requests
from bs4 import BeautifulSoup


# ============================================================
# SETTINGS
# ============================================================

USERNAME = "Arghya-03"

ROOT = Path(__file__).resolve().parent.parent

OUTPUT_FILE = ROOT / "data" / "contributions.json"

URL = f"https://github.com/users/{USERNAME}/contributions"


# ============================================================
# CREATE DATA DIRECTORY
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# FETCH GITHUB CONTRIBUTION CALENDAR
# ============================================================

print("----------------------------------------")
print("FETCHING GITHUB CONTRIBUTIONS")
print("----------------------------------------")

print(f"Username : {USERNAME}")
print(f"URL      : {URL}")
print()


headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html,application/xhtml+xml"
}


try:
    response = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

except requests.RequestException as error:

    print("ERROR: Could not fetch GitHub contributions.")
    print(error)

    raise SystemExit(1)


print(f"HTTP status: {response.status_code}")


# ============================================================
# PARSE HTML
# ============================================================

soup = BeautifulSoup(
    response.text,
    "html.parser"
)

days = []


# GitHub contribution cells
cells = soup.select("td[data-date]")

print(
    f"Contribution cells found: {len(cells)}"
)


# ============================================================
# READ CONTRIBUTION COUNTS FROM TOOLTIP
# ============================================================

tooltip_counts = {}


for tooltip in soup.select("tool-tip"):

    tooltip_for = tooltip.get("for")

    tooltip_text = tooltip.get_text(
        " ",
        strip=True
    )

    if not tooltip_for:
        continue

    # Examples:
    # "1 contribution on September 28, 2026"
    # "12 contributions on September 29, 2026"

    match = re.search(
        r"(\d+)\s+contribution",
        tooltip_text
    )

    if match:

        tooltip_counts[
            tooltip_for
        ] = int(match.group(1))


print(
    f"Contribution tooltips found: "
    f"{len(tooltip_counts)}"
)


# ============================================================
# EXTRACT CONTRIBUTION DAYS
# ============================================================

for cell in cells:

    date_value = cell.get("data-date")

    if not date_value:
        continue

    cell_id = cell.get("id")

    count = 0


    # --------------------------------------------------------
    # Method 1: Read count from associated tooltip
    # --------------------------------------------------------

    if cell_id:

        count = tooltip_counts.get(
            cell_id,
            0
        )


    # --------------------------------------------------------
    # Method 2: Try data-count if available
    # --------------------------------------------------------

    if count == 0:

        data_count = cell.get(
            "data-count"
        )

        if data_count is not None:

            try:

                count = int(
                    data_count
                )

            except ValueError:

                pass


    # --------------------------------------------------------
    # Method 3: Try aria-label
    # --------------------------------------------------------

    if count == 0:

        aria = cell.get(
            "aria-label",
            ""
        )

        match = re.search(
            r"(\d+)\s+contribution",
            aria
        )

        if match:

            count = int(
                match.group(1)
            )


    days.append({

        "date": date_value,

        "count": count

    })


# ============================================================
# VALIDATION
# ============================================================

if not days:

    print()
    print(
        "ERROR: No contribution days were found."
    )

    print(
        "GitHub's contribution HTML may have changed."
    )

    raise SystemExit(1)


# ============================================================
# REMOVE DUPLICATE DATES
# ============================================================

unique_days = {}


for day in days:

    unique_days[
        day["date"]
    ] = day["count"]


days = [

    {
        "date": day_date,
        "count": count
    }

    for day_date, count
    in sorted(
        unique_days.items()
    )

]


print(
    f"Unique contribution days: "
    f"{len(days)}"
)


# ============================================================
# CALCULATE STATISTICS
# ============================================================

counts = [

    day["count"]

    for day in days

]


total_contributions = sum(
    counts
)


# ============================================================
# BEST DAY
# ============================================================

best_day = max(
    days,
    key=lambda day: day["count"]
)


# ============================================================
# CURRENT STREAK
# ============================================================

current_streak = 0

today = date.today()


count_by_date = {

    day["date"]: day["count"]

    for day in days

}


check_date = today


while True:

    key = check_date.isoformat()

    if count_by_date.get(
        key,
        0
    ) > 0:

        current_streak += 1

        check_date -= timedelta(
            days=1
        )

    else:

        break


# ============================================================
# LONGEST STREAK
# ============================================================

longest_streak = 0

running_streak = 0

previous_date = None


for day in days:

    current_date = date.fromisoformat(
        day["date"]
    )


    if day["count"] > 0:

        if (

            previous_date is not None

            and current_date
            == previous_date
            + timedelta(days=1)

        ):

            running_streak += 1

        else:

            running_streak = 1


        longest_streak = max(
            longest_streak,
            running_streak
        )


        previous_date = current_date


    else:

        running_streak = 0

        previous_date = None


# ============================================================
# MONTHLY TOTALS
# ============================================================

monthly_totals = {}


for day in days:

    month = day["date"][:7]

    monthly_totals.setdefault(
        month,
        0
    )

    monthly_totals[
        month
    ] += day["count"]


# ============================================================
# FINAL JSON DATA
# ============================================================

data = {

    "username": USERNAME,

    "generated_at":
        date.today().isoformat(),

    "days": days,

    "stats": {

        "total_contributions":
            total_contributions,

        "current_streak":
            current_streak,

        "longest_streak":
            longest_streak,

        "best_day":
            best_day,

        "monthly_totals":
            monthly_totals

    }

}


# ============================================================
# WRITE JSON
# ============================================================

OUTPUT_FILE.write_text(

    json.dumps(
        data,
        indent=2
    ),

    encoding="utf-8"

)


# ============================================================
# RESULT
# ============================================================

print()

print("----------------------------------------")
print("CONTRIBUTION DATA CREATED")
print("----------------------------------------")

print(
    f"Output : {OUTPUT_FILE}"
)

print(
    f"Days   : {len(days)}"
)

print(
    f"Total  : {total_contributions}"
)

print(
    f"Current streak : {current_streak}"
)

print(
    f"Longest streak : {longest_streak}"
)

print(
    f"Best day       : "
    f"{best_day['date']} "
    f"({best_day['count']} contributions)"
)

print("----------------------------------------")