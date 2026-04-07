"""Optional ttkbootstrap GUI for the AFK Arena bot.

Simple control panel with task toggles and a Start/Stop button. Logs pipe
into a text area. Pattern inspired by Thoteman/AFKArenaAutomator.
"""

from __future__ import annotations

import threading
from queue import Queue, Empty

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import BOTH, LEFT, RIGHT, X, Y, NSEW, W, E, N, S
except ImportError:  # pragma: no cover
    raise SystemExit("ttkbootstrap not installed — install with `pip install ttkbootstrap`.")

from loguru import logger

from bot.config import load_config
from bot.adb import ADBController
from bot.vision import Vision
from bot.popup_handler import PopupHandler
from bot.navigator import Navigator
from bot.utils.logger import setup_logger
from bot.utils.state import BotState


class BotGUI:
    def __init__(self) -> None:
        self.cfg = load_config()
        setup_logger(self.cfg.bot.logs_dir)

        self.root = ttk.Window(title="AFK Arena Bot", themename="darkly", size=(780, 560))
        self.log_queue: Queue[str] = Queue()
        self._stop_flag = threading.Event()
        self._worker: threading.Thread | None = None

        self._build()
        self._attach_log_sink()
        self._poll_logs()

    # ------------------------------------------------------------------- UI
    def _build(self) -> None:
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=BOTH, expand=True)

        header = ttk.Label(frame, text="AFK Arena Bot", font=("Segoe UI", 18, "bold"))
        header.pack(anchor=W, pady=(0, 10))

        toggles = ttk.LabelFrame(frame, text="Tasks", padding=8)
        toggles.pack(fill=X, pady=5)
        self.vars = {
            "daily": ttk.BooleanVar(value=self.cfg.tasks.daily_tasks),
            "campaign": ttk.BooleanVar(value=self.cfg.tasks.campaign_push),
            "tower": ttk.BooleanVar(value=self.cfg.tasks.kings_tower),
            "arena": ttk.BooleanVar(value=self.cfg.tasks.arena),
            "guild": ttk.BooleanVar(value=self.cfg.tasks.guild_hunt),
            "store": ttk.BooleanVar(value=self.cfg.tasks.store_purchases),
            "labyrinth": ttk.BooleanVar(value=self.cfg.tasks.labyrinth),
        }
        for i, (k, var) in enumerate(self.vars.items()):
            ttk.Checkbutton(toggles, text=k.title(), variable=var).grid(
                row=i // 4, column=i % 4, sticky=W, padx=8, pady=4,
            )

        controls = ttk.Frame(frame)
        controls.pack(fill=X, pady=10)
        self.start_btn = ttk.Button(controls, text="Start", bootstyle="success", command=self.start)
        self.start_btn.pack(side=LEFT, padx=5)
        self.stop_btn = ttk.Button(controls, text="Stop", bootstyle="danger", command=self.stop, state="disabled")
        self.stop_btn.pack(side=LEFT, padx=5)
        ttk.Button(controls, text="Connect", command=self.test_connect).pack(side=LEFT, padx=5)
        ttk.Button(controls, text="Screenshot", command=self.take_screenshot).pack(side=LEFT, padx=5)

        log_frame = ttk.LabelFrame(frame, text="Log", padding=6)
        log_frame.pack(fill=BOTH, expand=True, pady=5)
        self.log_text = ttk.ScrolledText(log_frame, height=16, font=("Consolas", 9))
        self.log_text.pack(fill=BOTH, expand=True)

    # ------------------------------------------------------------- log sink
    def _attach_log_sink(self) -> None:
        def sink(msg):
            self.log_queue.put(str(msg))
        logger.add(sink, level="INFO", format="{time:HH:mm:ss} | {level: <7} | {message}")

    def _poll_logs(self) -> None:
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_text.insert("end", msg)
                self.log_text.see("end")
        except Empty:
            pass
        self.root.after(200, self._poll_logs)

    # -------------------------------------------------------------- actions
    def test_connect(self) -> None:
        try:
            adb = ADBController.from_config(self.cfg)
            adb.connect()
            shot = adb.screenshot()
            logger.info(f"connected — screenshot {shot.shape}")
        except Exception as e:
            logger.error(f"connect failed: {e}")

    def take_screenshot(self) -> None:
        import cv2
        from datetime import datetime
        try:
            adb = ADBController.from_config(self.cfg)
            adb.connect()
            shot = adb.screenshot()
            path = self.cfg.bot.errors_dir / f"gui_{datetime.now():%Y%m%d_%H%M%S}.png"
            cv2.imwrite(str(path), shot)
            logger.info(f"saved {path}")
        except Exception as e:
            logger.error(f"screenshot failed: {e}")

    def start(self) -> None:
        if self._worker and self._worker.is_alive():
            return
        self._stop_flag.clear()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker.start()

    def stop(self) -> None:
        self._stop_flag.set()
        self.stop_btn.configure(state="disabled")
        self.start_btn.configure(state="normal")
        logger.info("stop requested")

    def _worker_loop(self) -> None:
        try:
            adb = ADBController.from_config(self.cfg)
            adb.connect()
            vision = Vision(self.cfg.bot.images_dir)
            popup = PopupHandler(self.cfg.bot.errors_dir)
            nav = Navigator(popup)
            state = BotState(self.cfg.bot.state_db)

            from bot.tasks.daily import DailyTask
            from bot.tasks.campaign import CampaignTask
            from bot.tasks.tower import TowerTask

            if self.vars["daily"].get() and not self._stop_flag.is_set():
                DailyTask(adb, vision, popup, nav, state).run()
            if self.vars["campaign"].get() and not self._stop_flag.is_set():
                CampaignTask(
                    adb, vision, popup, nav, state,
                    max_retries=self.cfg.campaign.max_retries,
                    swap_formation_after=self.cfg.campaign.swap_formation_after,
                    give_up_after=self.cfg.campaign.give_up_after,
                    wait_hours_on_block=self.cfg.campaign.wait_hours_on_block,
                ).run()
            if self.vars["tower"].get() and not self._stop_flag.is_set():
                TowerTask(adb, vision, popup, nav, state).run()
            logger.info("worker done")
        except Exception as e:
            logger.exception(f"worker crashed: {e}")
        finally:
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    BotGUI().run()
