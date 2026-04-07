# AFK Arena Bot

Fully autonomous F2P speedrun bot for AFK Arena. Runs against an Android
emulator (BlueStacks / LDPlayer) on Windows using ADB + OpenCV template
matching. Handles rerolling, daily tasks, campaign pushing, tower pushing,
store purchases, and resource management — all via the optimal F2P strategy
baked into `bot/strategy/`.

> **Supports AFK Arena ONLY — not AFK Journey.**

## Features

- **ADB-driven input** — no Android SDK required (uses `adb` binary from
  Platform Tools)
- **OpenCV template matching** with cached templates and region-of-interest
  search
- **Universal popup handler** with a hard purchase-dialog blacklist so the bot
  can never spend real money
- **State machine navigator** that walks the menu graph from any screen back
  to the campaign
- **F2P strategy engine** — meta hero lists, wishlists, formations, SI/Furn
  priorities, store buy rules, diamond spending phases (1/2/3), RC Cramming
  logic
- **Full task suite** — daily loop, campaign push, King's Tower, Arena +
  Challenger, Arcane Labyrinth, Guild Hunt, bounty dispatch, smart summoning,
  hero leveling, redemption codes, events, **account reroll**
- **SQLite state persistence** — current chapter, hero roster, task history
- **Anti-detection** — randomized tap offsets (+/-5px), randomized delays
  (300-800ms), session/break scheduling (run 4-6 h, break 30-90 min, never
  24/7)
- **Kill switch** — Ctrl+C stops and disconnects cleanly
- **Typer CLI** + optional **ttkbootstrap GUI**
- **Guided setup** command to capture reference screenshots on first run

## Architecture

```
afk-arena-bot/
├── bot/
│   ├── config.py            # config.ini loader
│   ├── adb.py               # ADB controller (screenshot, tap, swipe)
│   ├── vision.py            # OpenCV matching + OCR
│   ├── popup_handler.py     # Universal popup dismissal with purchase blacklist
│   ├── navigator.py         # Screen detection + menu routing
│   ├── strategy/            # F2P meta, formations, resource rules, progression
│   ├── tasks/               # daily, campaign, tower, arena, guild, store,
│   │                        # bounty, summon, level_heroes, codes, reroll,
│   │                        # events, labyrinth
│   └── utils/               # logger, scheduler, state (SQLite)
├── images/                  # Reference screenshot library (populate via `setup`)
│   ├── buttons/  screens/  heroes/  popups/  icons/
├── cli.py                   # Typer CLI
├── gui.py                   # Optional ttkbootstrap GUI
├── config.ini               # Emulator port, task toggles, campaign rules
└── requirements.txt
```

## Prerequisites (Windows 10/11)

1. **Android Platform Tools** (ADB)  
   Download: <https://developer.android.com/tools/releases/platform-tools>  
   Extract to e.g. `C:\platform-tools\` and add to `PATH`. Verify:
   ```powershell
   adb version
   ```

2. **Python 3.10+**  
   <https://www.python.org/downloads/>

3. **Tesseract OCR** (optional, for reading numbers)  
   <https://github.com/UB-Mannheim/tesseract/wiki>

4. **Emulator** — BlueStacks 5 or LDPlayer 9  
   - Resolution: **1080x1920 portrait**
   - Enable ADB debugging in emulator settings
   - Install AFK Arena, set language to **English**

## Install

```powershell
git clone https://github.com/<your-user>/new-afk-arena-bot.git
cd new-afk-arena-bot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Edit `config.ini` with your emulator's ADB port (default 5555 for LDPlayer).

## First run

```powershell
python cli.py connect           # Verify ADB + screenshot works
python cli.py setup             # Guided capture of reference templates
python cli.py screenshot        # Dump a debug screenshot
```

Crop each captured screenshot in `images/` down to just the button/icon/screen
element you want matched. Better templates = higher match accuracy.

## Usage

```powershell
python cli.py run               # Full loop (daily + campaign + tower), forever
python cli.py daily             # Daily task loop only
python cli.py campaign          # Campaign push only
python cli.py tower             # King's Tower + Faction Towers
python cli.py reroll            # Reroll new account until Daimon/Rowan
python cli.py codes             # Enter redemption codes
python cli.py status            # Show persisted bot state
```

GUI:
```powershell
python gui.py
```

## Safety

- The popup handler maintains a **purchase blacklist** — any template named
  like `buy_now`, `purchase_button`, `diamond_spend_confirm`, `gem_purchase`,
  `paypal_button`, or `google_play_billing` causes the bot to press **BACK**
  instead of tapping.
- On an unknown screen, the bot presses BACK — never a blind confirm tap.
- Every unrecognized popup is screenshotted to `errors/` for manual review.
- Ctrl+C stops the bot and disconnects ADB immediately.

## Strategy notes

All F2P meta lives in `bot/strategy/`:

- `meta.py` — reroll targets, wishlists (early + mid), carry progression
  (Wukong -> Mirael -> Daimon), garrison priority, SI30/Furniture 9F lists,
  engraving caps (`Thoran: E11`), pre-built formations (`early_daimon`,
  `five_pull`, `ainz_comp`, `alna_grezhul`, `thoran_cheese`, `liberta_charm`)
- `resource_rules.py` — diamond spending phases 1-3 (summon-focused ->
  gear stall -> RC cramming), store buy rules (gold on essence + POE, diamonds
  on 5x Elite Soulstones + dust/EXP crates in phase 3), daily task order,
  campaign retry rules
- `progression.py` — phase detection and gating for RC cramming / summon
  behavior
- `formations.py` — pick ordered formations for the current chapter

Update these modules as the meta shifts — no code changes required in tasks.

## Credits

Patterns inspired by: Fortigate/AutoAFK, Thoteman/AFKArenaAutomator,
zebscripts/AFK-Daily.
