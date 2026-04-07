"""Bot configuration loaded from config.ini."""

from __future__ import annotations

import configparser
from pathlib import Path
from dataclasses import dataclass


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.ini"


@dataclass
class EmulatorConfig:
    host: str
    port: int

    @property
    def device(self) -> str:
        return f"{self.host}:{self.port}"


@dataclass
class GameConfig:
    width: int
    height: int
    package: str
    activity: str

    @property
    def component(self) -> str:
        return f"{self.package}/{self.activity}"


@dataclass
class BotConfig:
    session_hours: float
    break_minutes: float
    tap_randomize_px: int
    images_dir: Path
    errors_dir: Path
    logs_dir: Path
    state_db: Path


@dataclass
class TaskToggles:
    daily_tasks: bool
    campaign_push: bool
    kings_tower: bool
    arena: bool
    guild_hunt: bool
    store_purchases: bool
    labyrinth: bool
    bounty_board: bool
    summon: bool


@dataclass
class CampaignConfig:
    max_retries: int
    swap_formation_after: int
    give_up_after: int
    wait_hours_on_block: float


@dataclass
class Config:
    emulator: EmulatorConfig
    game: GameConfig
    bot: BotConfig
    tasks: TaskToggles
    campaign: CampaignConfig


def load_config(path: Path = CONFIG_PATH) -> Config:
    parser = configparser.ConfigParser()
    if not path.exists():
        raise FileNotFoundError(f"Missing config file: {path}")
    parser.read(path)

    emulator = EmulatorConfig(
        host=parser.get("emulator", "host"),
        port=parser.getint("emulator", "port"),
    )
    game = GameConfig(
        width=parser.getint("game", "width"),
        height=parser.getint("game", "height"),
        package=parser.get("game", "package"),
        activity=parser.get("game", "activity"),
    )
    bot = BotConfig(
        session_hours=parser.getfloat("bot", "session_hours"),
        break_minutes=parser.getfloat("bot", "break_minutes"),
        tap_randomize_px=parser.getint("bot", "tap_randomize_px"),
        images_dir=PROJECT_ROOT / parser.get("bot", "images_dir"),
        errors_dir=PROJECT_ROOT / parser.get("bot", "errors_dir"),
        logs_dir=PROJECT_ROOT / parser.get("bot", "logs_dir"),
        state_db=PROJECT_ROOT / parser.get("bot", "state_db"),
    )
    tasks = TaskToggles(
        daily_tasks=parser.getboolean("tasks", "daily_tasks"),
        campaign_push=parser.getboolean("tasks", "campaign_push"),
        kings_tower=parser.getboolean("tasks", "kings_tower"),
        arena=parser.getboolean("tasks", "arena"),
        guild_hunt=parser.getboolean("tasks", "guild_hunt"),
        store_purchases=parser.getboolean("tasks", "store_purchases"),
        labyrinth=parser.getboolean("tasks", "labyrinth"),
        bounty_board=parser.getboolean("tasks", "bounty_board"),
        summon=parser.getboolean("tasks", "summon"),
    )
    campaign = CampaignConfig(
        max_retries=parser.getint("campaign", "max_retries"),
        swap_formation_after=parser.getint("campaign", "swap_formation_after"),
        give_up_after=parser.getint("campaign", "give_up_after"),
        wait_hours_on_block=parser.getfloat("campaign", "wait_hours_on_block"),
    )

    for d in (bot.images_dir, bot.errors_dir, bot.logs_dir):
        d.mkdir(parents=True, exist_ok=True)

    return Config(emulator=emulator, game=game, bot=bot, tasks=tasks, campaign=campaign)
