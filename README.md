# Gacha Profile Viewer

A small website that visualizes gacha-game profile stats for:

- Genshin Impact
- Honkai: Star Rail — including Apocalyptic Shadow, Pure Fiction, Memory of Chaos, and Anomaly Arbitration
- Arknights: Endfield

Stats update automatically once a day via GitHub Actions, and daily primogem/jade income is tracked in per-game Excel diaries.

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
uv run main.py
```

`main.py` needs the following environment variables set (see `.github/workflows/update.yml` for how they're supplied in CI): `HOYOLAB_WEBHOOK`, `DISCORD_ID`, `HOYOLAB_USER_COOKIES`, `HOYOLAB_HSR_UID`, `HOYOLAB_GENSHIN_UID`, `ENDFIELD_WEBHOOK`, `ENDFIELD_CRED`, `ENDFIELD_GAME_ROLE`.

Lint and typecheck via [nox](https://nox.thea.codes/):

```bash
nox -s lint        # ruff
nox -s typecheck   # pyright
```

## How It Works

### Data Collection

The backend data is collected using Python.

- [`genshin.py`](https://github.com/seriaati/genshin.py) is used to authenticate and communicate with the official HoYoLAB endpoints for Genshin Impact and Honkai: Star Rail. It's pulled straight from GitHub `master` (pinned in `uv.lock`) rather than PyPI, to pick up recent fixes.
- Arknights: Endfield data comes from a small hand-rolled client (`scripts/endfield/client.py`) that talks directly to SKPort's API, since no public SDK exists for it yet.
- `httpx` handles all HTTP interactions (Discord webhooks, SKPort requests, image downloads), and `openpyxl` maintains the pull-income diary spreadsheets.
- The processed results are saved in the `data` folder to be used by the frontend, and a summary is posted to Discord via webhook.

The script `main.py` runs automatically every 24 hours via GitHub Actions.

## Future Improvements

- Wire up the Genshin character showcase (the grid exists in the markup but isn't populated yet)
- Cycle performance color indicator
- Statistics summary panel

## Disclaimer

This project is a fan-made viewer and is not affiliated with HoYoverse. All assets belong to their respective owners.
