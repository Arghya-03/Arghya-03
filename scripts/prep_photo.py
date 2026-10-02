from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


# --------------------------------------------------
# Paths
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

INPUT_FILE = ASSETS / "profile.jpg"
OUTPUT_FILE = ASSETS / "source-prepped.png"


# --------------------------------------------------
# Check input
# --------------------------------------------------

if not INPUT_FILE.exists():
    print(f"ERROR: Could not find {INPUT_FILE}")
    print("Make sure your photo is named 'arghya.jpg' inside the assets folder.")
    sys.exit(1)


print("Loading photo...")
print(f"Input : {INPUT_FILE}")
print(f"Output: {OUTPUT_FILE}")


# --------------------------------------------------
# 1. Remove background
# --------------------------------------------------

print("\n[1/4] Removing background...")

input_image = Image.open(INPUT_FILE).convert("RGBA")

foreground = remove(input_image)

# Convert to NumPy
rgba = np.array(foreground)

rgb = rgba[:, :, :3]
alpha = rgba[:, :, 3]

# --------------------------------------------------
# 2. Composite onto white
# --------------------------------------------------

print("[2/4] Creating white background...")

alpha_float = alpha.astype(np.float32) / 255.0

white = np.full_like(rgb, 255)

composited = (
    rgb.astype(np.float32) * alpha_float[:, :, None]
    + white.astype(np.float32) * (1 - alpha_float[:, :, None])
)

composited = np.clip(composited, 0, 255).astype(np.uint8)


# --------------------------------------------------
# 3. Convert to grayscale
# --------------------------------------------------

print("[3/4] Converting to grayscale...")

gray = cv2.cvtColor(composited, cv2.COLOR_RGB2GRAY)


# --------------------------------------------------
# 4. Improve local contrast using CLAHE
# --------------------------------------------------

print("[4/4] Improving contrast...")

clahe = cv2.createCLAHE(
    clipLimit=2.5,
    tileGridSize=(8, 8)
)

enhanced = clahe.apply(gray)


# --------------------------------------------------
# Save result
# --------------------------------------------------

result = Image.fromarray(enhanced)

result.save(
    OUTPUT_FILE,
    format="PNG",
    optimize=True
)

print("\n----------------------------------------")
print("SUCCESS!")
print("----------------------------------------")
print(f"Created: {OUTPUT_FILE}")
print("\nYour photo is now ready for ASCII conversion.")