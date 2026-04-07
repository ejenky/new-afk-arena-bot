"""Universal popup dismissal with hard purchase protection.

This is the most critical module in the bot — a single mistap on a diamond
confirm button can nuke weeks of progress. Rules:

    1. Known safe popups are dismissed via their known close/confirm templates.
    2. Purchase/payment templates are BLACKLISTED — never tapped.
    3. Unknown popups trigger BACK instead of a blind tap.
    4. Every unknown popup is screenshotted for manual review.
"""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
from loguru import logger


# (detection_template, optional_tap_template)
# If tap_template is None, tap the center of the detected match.
POPUP_PATTERNS: List[Tuple[str, Optional[str]]] = [
    ("popups/daily_login_claim.png", "popups/daily_login_claim.png"),
    ("popups/close_x.png", "popups/close_x.png"),
    ("popups/confirm_button.png", "popups/confirm_button.png"),
    ("popups/tap_to_continue.png", None),
    ("popups/level_up_ok.png", "popups/level_up_ok.png"),
    ("popups/rate_later.png", "popups/rate_later.png"),
    ("popups/special_offer_x.png", "popups/special_offer_x.png"),
    ("popups/event_popup_x.png", "popups/event_popup_x.png"),
    ("popups/reward_collected_ok.png", "popups/reward_collected_ok.png"),
    ("popups/skip.png", "popups/skip.png"),
]

# Templates that indicate a real-money or diamond-spending dialog. NEVER tap.
PURCHASE_BLACKLIST: List[str] = [
    "popups/buy_now.png",
    "popups/purchase_button.png",
    "popups/diamond_spend_confirm.png",
    "popups/gem_purchase.png",
    "popups/paypal_button.png",
    "popups/google_play_billing.png",
]

SAFE_TAP_POINT: Tuple[int, int] = (540, 1700)


class PopupHandler:
    def __init__(self, errors_dir: Path) -> None:
        self.errors_dir = Path(errors_dir)
        self.errors_dir.mkdir(parents=True, exist_ok=True)

    def _has_purchase_template(self, screenshot, vision) -> bool:
        for tmpl in PURCHASE_BLACKLIST:
            if not vision.template_exists(tmpl):
                continue
            if vision.find(screenshot, tmpl, confidence=0.82):
                logger.warning(f"Purchase dialog detected ({tmpl}) — pressing BACK")
                return True
        return False

    def _save_unknown(self, screenshot, label: str = "unknown_popup") -> Path:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.errors_dir / f"{label}_{ts}.png"
        try:
            cv2.imwrite(str(path), screenshot)
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
        return path

    def dismiss_all(self, adb, vision, max_attempts: int = 5) -> int:
        """Dismiss every popup we can identify. Returns count of popups dismissed."""
        dismissed = 0
        for _ in range(max_attempts):
            screenshot = adb.screenshot()

            # Hard rule: if a purchase dialog is on screen, press BACK immediately.
            if self._has_purchase_template(screenshot, vision):
                self._save_unknown(screenshot, "purchase_dialog_blocked")
                adb.back()
                time.sleep(1.2)
                continue

            found = False
            for detect_tmpl, tap_tmpl in POPUP_PATTERNS:
                match = vision.find(screenshot, detect_tmpl, confidence=0.82)
                if not match:
                    continue
                if tap_tmpl is None:
                    adb.tap(*SAFE_TAP_POINT)
                else:
                    tap_match = vision.find(screenshot, tap_tmpl, confidence=0.82)
                    if tap_match:
                        adb.tap(tap_match[0], tap_match[1])
                    else:
                        adb.tap(match[0], match[1])
                logger.info(f"Dismissed popup: {detect_tmpl}")
                dismissed += 1
                found = True
                time.sleep(1.5)
                break

            if not found:
                break
        return dismissed

    def handle_unknown(self, adb, vision, save: bool = True) -> None:
        """Called when we appear stuck on an unknown screen.

        Saves a screenshot and presses BACK — never a blind tap.
        """
        if save:
            screenshot = adb.screenshot()
            path = self._save_unknown(screenshot, "stuck_unknown")
            logger.warning(f"Unknown screen — saved {path}, pressing BACK")
        adb.back()
        time.sleep(1.0)
