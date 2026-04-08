"""AFK Arena Bot — Typer CLI entry point.

Usage:
    python cli.py run              # Full bot loop
    python cli.py daily            # Daily tasks only
    python cli.py campaign         # Campaign push only
    python cli.py tower            # King's Tower push
    python cli.py reroll           # Reroll new account
    python cli.py codes            # Enter redemption codes
    python cli.py screenshot       # Take debug screenshot
    python cli.py connect          # Test emulator connection
    python cli.py setup            # First-run guided image capture
    python cli.py status           # Show bot state
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer
from loguru import logger
from rich.console import Console
from rich.table import Table

from bot.config import load_config
from bot.adb import ADBController
from bot.vision import Vision
from bot.popup_handler import PopupHandler
from bot.navigator import Navigator
from bot.utils.logger import setup_logger
from bot.utils.state import BotState
from bot.utils.scheduler import SessionScheduler


app = typer.Typer(help="AFK Arena F2P autonomous bot.")
console = Console()


# ---------------------------------------------------------------- bootstrap
def _bootstrap(debug: bool = False):
    cfg = load_config()
    setup_logger(cfg.bot.logs_dir, level="DEBUG" if debug else "INFO")
    if debug:
        logger.info(f"DEBUG MODE — screenshots to {cfg.bot.debug_dir}, confidence logging on")
    adb = ADBController.from_config(cfg, debug=debug)
    adb.connect()
    vision = Vision(cfg.bot.images_dir, debug=debug)
    popup = PopupHandler(cfg.bot.errors_dir)
    nav = Navigator(popup)
    state = BotState(cfg.bot.state_db)
    return cfg, adb, vision, popup, nav, state


# ---------------------------------------------------------------- commands
@app.command()
def connect():
    """Connect to the emulator and verify ADB works."""
    cfg = load_config()
    setup_logger(cfg.bot.logs_dir)
    adb = ADBController.from_config(cfg)
    adb.connect()
    shot = adb.screenshot()
    console.print(f"[green]OK[/green] — connected to {cfg.emulator.device}, screenshot {shot.shape}")


@app.command()
def screenshot(name: str = typer.Option("debug", help="Filename stem")):
    """Save a screenshot from the emulator."""
    import cv2
    cfg, adb, _, _, _, _ = _bootstrap()
    shot = adb.screenshot()
    out = cfg.bot.errors_dir / f"{name}_{datetime.now():%Y%m%d_%H%M%S}.png"
    cv2.imwrite(str(out), shot)
    console.print(f"Saved: {out}")


_DEBUG_OPT = typer.Option(
    False, "--debug", "-d",
    help="Save before/after tap screenshots with red target rectangle, log every "
         "match confidence score, lower match threshold for visibility.",
)


@app.command()
def daily(debug: bool = _DEBUG_OPT):
    """Run daily task loop."""
    cfg, adb, vision, popup, nav, state = _bootstrap(debug=debug)
    from bot.tasks.daily import DailyTask
    DailyTask(adb, vision, popup, nav, state).run()


@app.command()
def campaign(debug: bool = _DEBUG_OPT):
    """Campaign push only."""
    cfg, adb, vision, popup, nav, state = _bootstrap(debug=debug)
    from bot.tasks.campaign import CampaignTask
    CampaignTask(
        adb, vision, popup, nav, state,
        max_retries=cfg.campaign.max_retries,
        swap_formation_after=cfg.campaign.swap_formation_after,
        give_up_after=cfg.campaign.give_up_after,
        wait_hours_on_block=cfg.campaign.wait_hours_on_block,
    ).run()


@app.command()
def tower(debug: bool = _DEBUG_OPT):
    """King's Tower + Faction Tower push."""
    cfg, adb, vision, popup, nav, state = _bootstrap(debug=debug)
    from bot.tasks.tower import TowerTask
    TowerTask(adb, vision, popup, nav, state).run()


@app.command()
def reroll(debug: bool = _DEBUG_OPT):
    """Reroll a new guest account until a target hero is pulled."""
    cfg, adb, vision, popup, nav, state = _bootstrap(debug=debug)
    from bot.tasks.reroll import RerollTask
    RerollTask(adb, vision, popup, nav, state).run()


@app.command()
def codes(debug: bool = _DEBUG_OPT):
    """Enter redemption codes."""
    cfg, adb, vision, popup, nav, state = _bootstrap(debug=debug)
    from bot.tasks.codes import CodesTask
    CodesTask(adb, vision, popup, nav, state).run()


@app.command()
def run(debug: bool = _DEBUG_OPT):
    """Full bot loop: daily tasks + campaign + tower, with session breaks."""
    cfg, adb, vision, popup, nav, state = _bootstrap(debug=debug)
    from bot.tasks.daily import DailyTask
    from bot.tasks.campaign import CampaignTask
    from bot.tasks.tower import TowerTask

    def session():
        if cfg.tasks.daily_tasks:
            DailyTask(adb, vision, popup, nav, state).run()
        if cfg.tasks.campaign_push:
            CampaignTask(
                adb, vision, popup, nav, state,
                max_retries=cfg.campaign.max_retries,
                swap_formation_after=cfg.campaign.swap_formation_after,
                give_up_after=cfg.campaign.give_up_after,
                wait_hours_on_block=cfg.campaign.wait_hours_on_block,
            ).run()
        if cfg.tasks.kings_tower:
            TowerTask(adb, vision, popup, nav, state).run()

    scheduler = SessionScheduler(cfg.bot.session_hours, cfg.bot.break_minutes)
    try:
        scheduler.run_forever(session)
    except KeyboardInterrupt:
        console.print("[yellow]stopping[/yellow]")
        adb.disconnect()


@app.command()
def status():
    """Show persisted bot state."""
    cfg = load_config()
    setup_logger(cfg.bot.logs_dir)
    state = BotState(cfg.bot.state_db)
    all_state = state.all_state()
    table = Table(title="Bot State")
    table.add_column("Key")
    table.add_column("Value")
    for k, v in all_state.items():
        table.add_row(k, str(v))
    console.print(table)

    table2 = Table(title="Recent Tasks")
    table2.add_column("Task")
    table2.add_column("Status")
    table2.add_column("Timestamp")
    table2.add_column("Details")
    for row in state.recent_tasks(15):
        table2.add_row(*(str(c) for c in row))
    console.print(table2)


@app.command()
def setup():
    """First-run: guided image capture — save screenshots for templates."""
    import cv2
    cfg, adb, vision, _, _, _ = _bootstrap()
    console.print("[bold]Guided setup[/bold] — navigate to each screen when prompted.")
    prompts = [
        ("screens/main_menu.png", "Main menu (campaign bottom tab selected)"),
        ("screens/campaign_map.png", "Campaign map"),
        ("screens/dark_forest.png", "Dark Forest"),
        ("screens/ranhorn.png", "Ranhorn city"),
        ("screens/victory.png", "Victory screen (use any won battle)"),
        ("screens/defeat.png", "Defeat screen"),
        ("buttons/battle_begin.png", "Battle 'Begin' button"),
        ("buttons/stage_challenge.png", "Stage 'Challenge' button"),
    ]
    for name, desc in prompts:
        out = cfg.bot.images_dir / name
        out.parent.mkdir(parents=True, exist_ok=True)
        typer.prompt(f"[{name}] Navigate to: {desc}. Press Enter to capture", default="")
        shot = adb.screenshot()
        cv2.imwrite(str(out), shot)
        console.print(f"  saved {out}")
    console.print("[green]Setup complete. Crop each saved screenshot to the element in question.[/green]")


if __name__ == "__main__":
    app()
