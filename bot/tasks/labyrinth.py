"""Arcane Labyrinth / Dismal Maze automation — best-effort navigation."""

from __future__ import annotations

import time

from .base import BaseTask


class LabyrinthTask(BaseTask):
    name = "labyrinth"

    def run(self) -> bool:
        self.log("starting Arcane Labyrinth run")
        if not self.nav.goto_labyrinth(self.adb, self.vision):
            return False
        self.popup.dismiss_all(self.adb, self.vision)

        # Enter the lower-tier maze (Dismal) for guaranteed daily clear.
        if not self.vision.wait_and_tap(self.adb, "buttons/lab_enter.png", timeout=5):
            self.log("lab enter button not found")
            return False

        for step in range(30):
            self.popup.dismiss_all(self.adb, self.vision)
            shot = self.adb.screenshot()

            # Pick up rewards if present.
            if self.vision.find_and_tap(self.adb, shot, "buttons/lab_collect.png", 0.82):
                time.sleep(0.8)
                continue

            # Battle room — tap begin, wait for result.
            if self.vision.find_and_tap(self.adb, shot, "buttons/battle_begin.png", 0.82):
                time.sleep(45)
                self.popup.dismiss_all(self.adb, self.vision)
                continue

            # Move toward next unvisited tile (center-up).
            self.adb.tap(540, 900)
            time.sleep(1.0)

            if self.vision.find(shot, "screens/lab_complete.png", 0.82):
                self.log("labyrinth complete")
                break

        # Collect lab store purchases via Store task for labyrinth-specific items.
        self._record("labyrinth", "completed daily run")
        return True
