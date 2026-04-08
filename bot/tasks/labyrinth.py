"""Arcane Labyrinth / Dismal Maze — coordinate-driven daily run."""

from __future__ import annotations

import time

from .base import BaseTask
from .. import coords


class LabyrinthTask(BaseTask):
    name = "labyrinth"

    def _dismiss(self) -> None:
        self.popup.dismiss_all(self.adb, self.vision)

    def run(self) -> bool:
        self.log("starting Arcane Labyrinth run")
        self.nav.goto_labyrinth(self.adb, self.vision)
        time.sleep(1.0)
        self._dismiss()

        # Enter the lower-tier Dismal Maze for a guaranteed daily clear.
        self.adb.tap(*coords.LAB_DISMAL_MAZE)
        time.sleep(1.0)
        self.adb.tap(*coords.LAB_ENTER)
        time.sleep(1.5)
        self._dismiss()

        # Greedy walk: tap center, begin any battle encountered, repeat.
        for _ in range(30):
            self._dismiss()
            self.adb.tap(*coords.LAB_BEGIN)
            time.sleep(1.0)
            # Battle might have started — wait briefly for auto-completion.
            time.sleep(25)
            self._dismiss()
            self.adb.tap(*coords.LAB_MOVE_UP)
            time.sleep(1.0)

        self._record("labyrinth", "daily run attempted")
        return True
