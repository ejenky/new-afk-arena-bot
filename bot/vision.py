"""OpenCV-based vision: template matching, color checks, OCR, wait helpers."""

from __future__ import annotations

import time
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np
from loguru import logger


Match = Tuple[int, int, int, int, float]  # (cx, cy, w, h, confidence)


class TemplateMissingError(FileNotFoundError):
    pass


class Vision:
    def __init__(self, images_dir: Path) -> None:
        self.images_dir = Path(images_dir)
        self._cache: dict[str, np.ndarray] = {}

    # --------------------------------------------------------------- loading
    def load_template(self, name: str) -> np.ndarray:
        if name in self._cache:
            return self._cache[name]
        path = self.images_dir / name
        if not path.exists():
            raise TemplateMissingError(f"Template not found: {path}")
        img = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if img is None:
            raise TemplateMissingError(f"Failed to read template: {path}")
        self._cache[name] = img
        return img

    def template_exists(self, name: str) -> bool:
        return (self.images_dir / name).exists()

    # ---------------------------------------------------------------- search
    def find(
        self,
        screenshot: np.ndarray,
        template_name: str,
        confidence: float = 0.85,
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> Optional[Match]:
        try:
            template = self.load_template(template_name)
        except TemplateMissingError:
            return None

        haystack = screenshot
        offset_x = offset_y = 0
        if region is not None:
            x, y, w, h = region
            haystack = screenshot[y:y + h, x:x + w]
            offset_x, offset_y = x, y

        if haystack.shape[0] < template.shape[0] or haystack.shape[1] < template.shape[1]:
            return None

        result = cv2.matchTemplate(haystack, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val < confidence:
            return None
        h, w = template.shape[:2]
        cx = max_loc[0] + w // 2 + offset_x
        cy = max_loc[1] + h // 2 + offset_y
        return (cx, cy, w, h, float(max_val))

    def find_all(
        self,
        screenshot: np.ndarray,
        template_name: str,
        confidence: float = 0.85,
    ) -> List[Tuple[int, int]]:
        try:
            template = self.load_template(template_name)
        except TemplateMissingError:
            return []
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        ys, xs = np.where(result >= confidence)
        h, w = template.shape[:2]
        matches = [(int(x + w // 2), int(y + h // 2)) for x, y in zip(xs, ys)]
        # Deduplicate matches within 20px of each other.
        filtered: List[Tuple[int, int]] = []
        for m in matches:
            if not any(abs(m[0] - f[0]) < 20 and abs(m[1] - f[1]) < 20 for f in filtered):
                filtered.append(m)
        return filtered

    # ----------------------------------------------------------------- pixel
    def pixel_matches(
        self,
        screenshot: np.ndarray,
        x: int,
        y: int,
        expected_rgb: Tuple[int, int, int],
        tolerance: int = 15,
    ) -> bool:
        # Screenshots from ADBController are BGR.
        b, g, r = (int(c) for c in screenshot[y, x, :3])
        actual = (r, g, b)
        return all(abs(a - e) <= tolerance for a, e in zip(actual, expected_rgb))

    # ------------------------------------------------------------------ wait
    def wait_for(
        self,
        adb,
        template_name: str,
        timeout: float = 30,
        confidence: float = 0.85,
        poll_interval: float = 1.0,
    ) -> Optional[Match]:
        start = time.time()
        while time.time() - start < timeout:
            match = self.find(adb.screenshot(), template_name, confidence)
            if match:
                return match
            time.sleep(poll_interval)
        logger.debug(f"wait_for timeout: {template_name}")
        return None

    def wait_and_tap(
        self,
        adb,
        template_name: str,
        timeout: float = 30,
        confidence: float = 0.85,
    ) -> bool:
        match = self.wait_for(adb, template_name, timeout, confidence)
        if match:
            adb.tap(match[0], match[1])
            return True
        return False

    def find_and_tap(
        self,
        adb,
        screenshot: np.ndarray,
        template_name: str,
        confidence: float = 0.85,
    ) -> bool:
        match = self.find(screenshot, template_name, confidence)
        if match:
            adb.tap(match[0], match[1])
            return True
        return False

    # ------------------------------------------------------------------- OCR
    def read_text(self, screenshot: np.ndarray, region: Optional[Tuple[int, int, int, int]] = None) -> str:
        try:
            import pytesseract
        except ImportError:
            logger.warning("pytesseract not installed; OCR unavailable")
            return ""
        crop = screenshot
        if region is not None:
            x, y, w, h = region
            crop = screenshot[y:y + h, x:x + w]
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        try:
            return pytesseract.image_to_string(thresh).strip()
        except Exception as e:
            logger.warning(f"OCR failed: {e}")
            return ""
