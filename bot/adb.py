"""ADB controller — screenshots, taps, swipes, app management.

All actions are jittered with random offsets and delays for anti-detection.
"""

from __future__ import annotations

import io
import random
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import Image
from loguru import logger


class ADBError(RuntimeError):
    pass


class ADBController:
    def __init__(
        self,
        port: int = 5555,
        host: str = "127.0.0.1",
        randomize_px: int = 5,
        package: str = "com.lilithgame.hgame.gp",
        activity: str = "com.lilithgame.hgame.GameActivity",
        debug: bool = False,
        debug_dir: Optional[Path] = None,
    ) -> None:
        self.host = host
        self.port = port
        self.device = f"{host}:{port}"
        self.randomize_px = randomize_px
        self.package = package
        self.activity = activity
        self.debug = debug
        self.debug_dir = Path(debug_dir) if debug_dir else Path("debug")
        if self.debug:
            self.debug_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"ADB debug mode ON — saving screenshots to {self.debug_dir}")
        self._connected = False

    # ------------------------------------------------------------------ core
    def _adb(self, *args: str, capture: bool = True, timeout: int = 30) -> subprocess.CompletedProcess:
        cmd = ["adb", "-s", self.device, *args]
        try:
            return subprocess.run(cmd, capture_output=capture, timeout=timeout)
        except FileNotFoundError as e:
            raise ADBError("`adb` not found in PATH. Install Android Platform Tools.") from e
        except subprocess.TimeoutExpired as e:
            raise ADBError(f"adb command timed out: {' '.join(cmd)}") from e

    def connect(self) -> None:
        try:
            result = subprocess.run(
                ["adb", "connect", self.device], capture_output=True, text=True, timeout=15
            )
        except FileNotFoundError as e:
            raise ADBError("`adb` not found in PATH. Install Android Platform Tools.") from e
        out = (result.stdout or "") + (result.stderr or "")
        if "connected" not in out.lower() and "already" not in out.lower():
            raise ADBError(f"Failed to connect to {self.device}: {out.strip()}")
        self._connected = True
        logger.info(f"ADB connected to {self.device}")

    def disconnect(self) -> None:
        try:
            subprocess.run(["adb", "disconnect", self.device], capture_output=True, timeout=5)
        except Exception:
            pass
        self._connected = False
        logger.info(f"ADB disconnected from {self.device}")

    def ensure_connected(self) -> None:
        if not self._connected:
            self.connect()

    # ----------------------------------------------------------- screenshots
    def screenshot(self) -> np.ndarray:
        self.ensure_connected()
        result = self._adb("exec-out", "screencap", "-p", timeout=15)
        if not result.stdout:
            raise ADBError("Empty screenshot from device")
        try:
            image = Image.open(io.BytesIO(result.stdout)).convert("RGB")
        except Exception as e:
            raise ADBError(f"Failed to decode screenshot: {e}") from e
        # OpenCV uses BGR; convert from PIL RGB.
        arr = np.array(image)
        return arr[:, :, ::-1].copy()  # RGB -> BGR

    # --------------------------------------------------------- debug helpers
    def _save_tap_debug(self, x: int, y: int, label: str, ts: str, draw_target: bool) -> None:
        """Save a debug screenshot of the current frame.

        If draw_target is True, overlays a red rectangle and crosshair on (x, y).
        Used before/after every tap when debug mode is on.
        """
        try:
            shot = self.screenshot()
        except Exception as e:
            logger.warning(f"debug screenshot grab failed: {e}")
            return
        if draw_target:
            size = 60
            cv2.rectangle(
                shot,
                (x - size // 2, y - size // 2),
                (x + size // 2, y + size // 2),
                (0, 0, 255),  # BGR red
                4,
            )
            cv2.line(shot, (x - size, y), (x + size, y), (0, 0, 255), 2)
            cv2.line(shot, (x, y - size), (x, y + size), (0, 0, 255), 2)
        path = self.debug_dir / f"tap_{ts}_{label}_{x}x{y}.png"
        try:
            cv2.imwrite(str(path), shot)
            logger.info(f"debug: {path.name}")
        except Exception as e:
            logger.warning(f"debug screenshot save failed: {e}")

    # ----------------------------------------------------------------- taps
    def tap(self, x: int, y: int, randomize: bool = True, post_delay: bool = True) -> None:
        self.ensure_connected()
        if randomize and self.randomize_px > 0:
            x += random.randint(-self.randomize_px, self.randomize_px)
            y += random.randint(-self.randomize_px, self.randomize_px)

        ts = ""
        if self.debug:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            self._save_tap_debug(x, y, "before", ts, draw_target=True)

        log_fn = logger.info if self.debug else logger.debug
        log_fn(f"tap ({x},{y})")
        self._adb("shell", "input", "tap", str(x), str(y))
        if post_delay:
            time.sleep(random.uniform(0.3, 0.8))

        if self.debug:
            self._save_tap_debug(x, y, "after", ts, draw_target=False)

    def long_press(self, x: int, y: int, duration_ms: int = 1000) -> None:
        self.swipe(x, y, x, y, duration_ms=duration_ms)

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 500) -> None:
        self.ensure_connected()
        logger.debug(f"swipe ({x1},{y1})->({x2},{y2}) {duration_ms}ms")
        self._adb(
            "shell", "input", "swipe",
            str(x1), str(y1), str(x2), str(y2), str(duration_ms),
        )
        time.sleep(random.uniform(0.5, 1.0))

    def back(self) -> None:
        self.ensure_connected()
        logger.debug("back")
        self._adb("shell", "input", "keyevent", "4")
        time.sleep(0.5)

    def home(self) -> None:
        self.ensure_connected()
        self._adb("shell", "input", "keyevent", "3")
        time.sleep(0.5)

    def text_input(self, text: str) -> None:
        self.ensure_connected()
        # adb shell input text uses %s for spaces and requires escaping certain chars.
        escaped = (
            text.replace("\\", "\\\\")
            .replace(" ", "%s")
            .replace("&", "\\&")
            .replace("'", "\\'")
            .replace('"', '\\"')
        )
        self._adb("shell", "input", "text", escaped)
        time.sleep(0.4)

    # ----------------------------------------------------------------- apps
    def launch_game(self) -> None:
        self.ensure_connected()
        logger.info(f"Launching {self.package}")
        self._adb("shell", "am", "start", "-n", f"{self.package}/{self.activity}")
        time.sleep(15)

    def kill_game(self) -> None:
        self.ensure_connected()
        logger.info(f"Killing {self.package}")
        self._adb("shell", "am", "force-stop", self.package)
        time.sleep(2)

    def is_game_running(self) -> bool:
        self.ensure_connected()
        result = self._adb("shell", "pidof", self.package)
        return bool(result.stdout and result.stdout.strip())

    # ------------------------------------------------------------- factories
    @classmethod
    def from_config(cls, cfg, debug: bool = False) -> "ADBController":
        return cls(
            host=cfg.emulator.host,
            port=cfg.emulator.port,
            randomize_px=cfg.bot.tap_randomize_px,
            package=cfg.game.package,
            activity=cfg.game.activity,
            debug=debug,
            debug_dir=getattr(cfg.bot, "debug_dir", None),
        )
