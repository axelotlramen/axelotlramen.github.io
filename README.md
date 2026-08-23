# axelotlramen's Gacha Dashboard

Public static frontend for my (axelotlramen's) personal gacha stats dashboard — Genshin Impact, Honkai: Star Rail, and Arknights: Endfield. The data pipeline that produces `data/stats.json` and `data/endgame_history.csv` lives in the private `gacha-stats-backend` repo (included here as a submodule) and isn't public, since it hand-rolls auth against undocumented APIs.

Built with vanilla HTML, CSS, and JS — no build step for the markup itself.

## Running locally

```bash
python3 -m http.server 8000
