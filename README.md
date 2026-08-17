# axelotlramen's Gacha Dashboard

This is my (axelotlramen's) personal dashboard for tracking my own progress across:

- Genshin Impact
- Honkai: Star Rail — including Apocalyptic Shadow, Pure Fiction, Memory of Chaos, and Anomaly Arbitration
- Arknights: Endfield

It's not a general-purpose tool for other players to plug their own accounts into — it's wired directly to my own HoYoLab/SKPort accounts. The rest of this README is here for my own future reference (and anyone curious how it's built), documenting how the whole thing works.

My stats update automatically once a day via GitHub Actions, and my daily primogem/jade income is tracked in per-game Excel diaries. I also run a separate pipeline that logs my HSR endgame (Apocalyptic Shadow/Pure Fiction/Memory of Chaos/Anomaly Arbitration) results into a personal Google Sheet, so I can track my own team usage and scores over time.

Built using vanilla HTML, CSS, and JavaScript for the frontend, with a Python automation pipeline (managed by [uv](https://docs.astral.sh/uv/)) collecting the data.

## Running locally

Frontend (static, no build step):

```bash
python3 -m http.server 8000
```

and open `http://localhost:8000`, which redirects to `http://localhost:8000/home/`. The site is a real multi-page site — Home, HSR, Genshin, and Endfield each live at their own URL (`/home/`, `/hsr/`, `/genshin/`, `/endfield/`).

Backend pipeline:

```bash
uv sync
uv run python -m scripts.update_stats
```

`scripts/update_stats.py` needs the following environment variables set (see `.github/workflows/update.yml` for how they're supplied in CI): `HOYOLAB_WEBHOOK`, `DISCORD_ID`, `HOYOLAB_USER_COOKIES`, `HOYOLAB_HSR_UID`, `HOYOLAB_GENSHIN_UID`, `ENDFIELD_WEBHOOK`, `ENDFIELD_CRED`, `ENDFIELD_GAME_ROLE`.

There's also a separate HSR endgame-to-Google-Sheets pipeline (`scripts/sheets/`, entrypoints `scripts/update_sheet.py` and `scripts/update_usage.py`), on its own daily/weekly schedule — see `.github/workflows/update-sheet.yml` and `update-weekly-usage.yml` for its required secrets.

Lint, typecheck, and test via [nox](https://nox.thea.codes/):

```bash
nox -s lint        # ruff
nox -s typecheck   # pyright
nox -s test        # pytest
```

## How It Works

### Data Collection

My backend data is collected using Python.

- [`genshin.py`](https://github.com/seriaati/genshin.py) is used to authenticate and communicate with the official HoYoLAB endpoints for Genshin Impact and Honkai: Star Rail. It's pulled straight from GitHub `master` (pinned in `uv.lock`) rather than PyPI, to pick up recent fixes.
- Arknights: Endfield data comes from a small hand-rolled client (`scripts/endfield/client.py`) that talks directly to SKPort's API, since no public SDK exists for it yet. Character/weapon images are hotlinked directly from SKPort rather than cached locally.
- `httpx` handles all HTTP interactions (Discord webhooks, SKPort requests), and `openpyxl` maintains the pull-income diary spreadsheets.
- The processed results are saved in the `data` folder to be used by the frontend, and a summary is posted to Discord via webhook.

`scripts/update_stats.py` runs automatically every 24 hours via GitHub Actions.

## Future Improvements

- Cycle performance color indicator
- Statistics summary panel

## Disclaimer

This is a personal fan-made project and isn't affiliated with HoYoverse or Arknights: Endfield's publishers. All assets belong to their respective owners.
