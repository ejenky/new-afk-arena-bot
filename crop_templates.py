"""Auto-crop setup screenshots into small template regions for OpenCV matchTemplate.

Run this on the Windows machine *after* `python cli.py setup` has saved full-screen
1080x1920 reference images into images/screens/ and images/buttons/.

For each target:
  - Attempts to auto-detect the region of interest using color thresholding
    (blue buttons) or contour/luminance detection (banners, tabs).
  - Falls back to a hardcoded crop box if detection fails.
  - Shows a matplotlib preview of the proposed crop.
  - Saves the crop *over* the original full-screen image.

Usage:
    python crop_templates.py                 # prompts before each save
    python crop_templates.py --yes           # accepts all auto-crops
    python crop_templates.py --no-preview    # skips matplotlib previews
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Tuple

import cv2
import numpy as np


# Portrait 1080 wide x 1920 tall (phone orientation).
SCREEN_W = 1080
SCREEN_H = 1920

IMAGES_DIR = Path(__file__).resolve().parent / "images"


BBox = Tuple[int, int, int, int]  # (x, y, w, h)


# ---------------------------------------------------------------------------
# Detection helpers
# ---------------------------------------------------------------------------
def _find_blue_button(img: np.ndarray, search_region: BBox) -> Optional[BBox]:
    """Find the largest blue-hued contour inside search_region.

    AFK Arena's primary action buttons are a saturated teal/blue gradient.
    Returns a (x, y, w, h) bbox in the full-image coordinate system, or None.
    """
    x, y, w, h = search_region
    roi = img[y:y + h, x:x + w]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    # Wide-ish range covering teal/cyan/blue button colors.
    lower = np.array([85, 90, 90])
    upper = np.array([130, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    # Keep reasonably sized blobs (buttons are ~150-400 px wide).
    good = [c for c in contours if 100 < cv2.boundingRect(c)[2] < 600
            and 30 < cv2.boundingRect(c)[3] < 200]
    if not good:
        return None
    biggest = max(good, key=cv2.contourArea)
    bx, by, bw, bh = cv2.boundingRect(biggest)
    # Shrink to the tight center to avoid catching the button's outer glow.
    pad_x = int(bw * 0.05)
    pad_y = int(bh * 0.05)
    return (x + bx + pad_x, y + by + pad_y,
            max(bw - 2 * pad_x, 10), max(bh - 2 * pad_y, 10))


def _find_bright_banner(img: np.ndarray, search_region: BBox) -> Optional[BBox]:
    """Find the brightest/largest text banner blob in search_region.

    Used for Victory/Defeat banners which are high-contrast white/yellow text.
    """
    x, y, w, h = search_region
    roi = img[y:y + h, x:x + w]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, np.ones((15, 25), np.uint8))
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    good = [c for c in contours if cv2.boundingRect(c)[2] > 150
            and cv2.boundingRect(c)[3] > 40]
    if not good:
        return None
    biggest = max(good, key=cv2.contourArea)
    bx, by, bw, bh = cv2.boundingRect(biggest)
    return (x + bx, y + by, bw, bh)


def _fallback_crop(box: BBox) -> Callable[[np.ndarray], Optional[BBox]]:
    """Return a detector that always yields the given fixed bbox."""
    def _detect(_img: np.ndarray) -> Optional[BBox]:
        return box
    return _detect


def _detector_button_bottom(img: np.ndarray) -> Optional[BBox]:
    """Blue action button in the bottom ~20% of the screen."""
    region = (100, int(SCREEN_H * 0.78), SCREEN_W - 200, int(SCREEN_H * 0.18))
    return _find_blue_button(img, region)


def _detector_bottom_nav(tab_index: int) -> Callable[[np.ndarray], Optional[BBox]]:
    """Crop one of the 5 bottom-nav tab icons.

    Bottom nav occupies approximately y=1760..1920, x=0..1080, split into 5 tabs.
    """
    def _detect(_img: np.ndarray) -> Optional[BBox]:
        tab_w = SCREEN_W // 5
        cx = tab_w * tab_index + tab_w // 2
        w, h = 100, 80
        return (cx - w // 2, 1780, w, h)
    return _detect


def _detector_screen_header(img: np.ndarray) -> Optional[BBox]:
    """Brightest text blob near the top of the screen (header title)."""
    region = (150, 80, SCREEN_W - 300, 180)
    return _find_bright_banner(img, region)


def _detector_victory_banner(img: np.ndarray) -> Optional[BBox]:
    region = (150, 300, SCREEN_W - 300, 400)
    return _find_bright_banner(img, region)


def _detector_defeat_banner(img: np.ndarray) -> Optional[BBox]:
    region = (150, 300, SCREEN_W - 300, 400)
    return _find_bright_banner(img, region)


def _detector_afk_chest(img: np.ndarray) -> Optional[BBox]:
    """AFK chest/World Map region — roughly center-bottom of campaign screen."""
    # Chest sits around y~1400 on campaign map at 1080x1920.
    return (390, 1350, 300, 160)


# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------
@dataclass
class CropTarget:
    path: str
    description: str
    detector: Callable[[np.ndarray], Optional[BBox]]
    fallback: BBox  # Used if detector returns None.


TARGETS = [
    CropTarget(
        path="buttons/battle_begin.png",
        description="Blue 'Begin' / 'Battle' button at bottom center",
        detector=_detector_button_bottom,
        fallback=(440, 1700, 200, 80),
    ),
    CropTarget(
        path="buttons/stage_challenge.png",
        description="Glowing 'Begin' button on campaign map",
        detector=_detector_button_bottom,
        fallback=(440, 1680, 200, 80),
    ),
    CropTarget(
        path="screens/main_menu.png",
        description="Campaign bottom-nav tab icon",
        detector=_detector_bottom_nav(tab_index=2),  # center tab
        fallback=(490, 1780, 100, 80),
    ),
    CropTarget(
        path="screens/campaign_map.png",
        description="AFK chest / 'World Map' region",
        detector=_detector_afk_chest,
        fallback=(465, 1370, 150, 80),
    ),
    CropTarget(
        path="screens/dark_forest.png",
        description="'Dark Forest' header text",
        detector=_detector_screen_header,
        fallback=(465, 110, 150, 50),
    ),
    CropTarget(
        path="screens/ranhorn.png",
        description="'Ranhorn' header text",
        detector=_detector_screen_header,
        fallback=(465, 110, 150, 50),
    ),
    CropTarget(
        path="screens/victory.png",
        description="'Victory' banner near top",
        detector=_detector_victory_banner,
        fallback=(390, 380, 300, 120),
    ),
    CropTarget(
        path="screens/defeat.png",
        description="'Defeat' banner near top",
        detector=_detector_defeat_banner,
        fallback=(390, 380, 300, 120),
    ),
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def _clamp_bbox(box: BBox, img_shape: Tuple[int, int]) -> BBox:
    h, w = img_shape[:2]
    x, y, bw, bh = box
    x = max(0, min(x, w - 1))
    y = max(0, min(y, h - 1))
    bw = max(1, min(bw, w - x))
    bh = max(1, min(bh, h - y))
    return (x, y, bw, bh)


def _preview(img: np.ndarray, box: BBox, title: str) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("  [preview skipped: matplotlib not installed]")
        return

    x, y, w, h = box
    overlay = img.copy()
    cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 255, 0), 6)
    crop = img[y:y + h, x:x + w]

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    axes[0].imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
    axes[0].set_title(f"{title}\nbbox = {box}")
    axes[0].axis("off")
    axes[1].imshow(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
    axes[1].set_title(f"crop {w}x{h}")
    axes[1].axis("off")
    plt.tight_layout()
    plt.show()


def crop_target(target: CropTarget, *, preview: bool, auto_yes: bool) -> bool:
    path = IMAGES_DIR / target.path
    if not path.exists() or path.stat().st_size == 0:
        print(f"[skip] {target.path} — file missing or empty. Run `python cli.py setup` first.")
        return False

    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        print(f"[skip] {target.path} — cv2 failed to read.")
        return False

    h, w = img.shape[:2]
    if (w, h) != (SCREEN_W, SCREEN_H):
        print(f"[warn] {target.path}: expected {SCREEN_W}x{SCREEN_H}, got {w}x{h}")

    bbox = target.detector(img)
    source = "auto"
    if bbox is None:
        bbox = target.fallback
        source = "fallback"
    bbox = _clamp_bbox(bbox, img.shape)

    print(f"[{target.path}] {target.description}")
    print(f"  bbox = {bbox}  ({source})")

    if preview:
        _preview(img, bbox, target.path)

    if not auto_yes:
        answer = input("  save this crop? [Y/n]: ").strip().lower()
        if answer == "n":
            print("  skipped")
            return False

    x, y, cw, ch = bbox
    crop = img[y:y + ch, x:x + cw]
    cv2.imwrite(str(path), crop)
    print(f"  saved -> {path}  ({cw}x{ch})")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto-crop AFK Arena reference templates.")
    parser.add_argument("--yes", action="store_true", help="Accept every auto-crop without prompting.")
    parser.add_argument("--no-preview", action="store_true", help="Skip matplotlib previews.")
    args = parser.parse_args()

    print(f"Images dir: {IMAGES_DIR}")
    saved = 0
    for target in TARGETS:
        try:
            if crop_target(target, preview=not args.no_preview, auto_yes=args.yes):
                saved += 1
        except KeyboardInterrupt:
            print("\ninterrupted")
            break
        except Exception as e:
            print(f"  ERROR on {target.path}: {e}")
    print(f"\nDone. {saved}/{len(TARGETS)} templates cropped.")


if __name__ == "__main__":
    main()
