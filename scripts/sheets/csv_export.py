"""Builds data/endgame_history.csv from the live Google Sheet for the website's
filterable endgame history view (mode, boss, characters used).

Boss name is taken directly from the Sheet's own manually-verified Boss column (left
blank if not filled in yet - never guessed here). The icon is then looked up by that
exact name via boss_lookup.py's monster-name index, rather than trusting boss_lookup's
own wave-position guess for the icon too - a fight can have more than one boss/elite-rank
enemy (e.g. a boss that summons another named add), so the guess sometimes points at the
wrong one even after the name itself has been manually corrected. A literal "Elite
Enemies" entry instead gets a representative Elite-rank icon from that stage's last wave.
"""

import csv
import logging
from datetime import date, datetime
from pathlib import Path

import genshin

from scripts.constants import HSR_SHORT_NAMES
from scripts.sheets.boss_lookup import BossLookup, character_icon_url
from scripts.sheets.nanoka import NanokaCharacterData
from scripts.sheets.sheets_client import DATE_COL, MODE_COL, NOTES_COL, SCORE_COL, SIDE_COL, VERSION_COL, GoogleSheetsClient

logger = logging.getLogger("csv_export")

OUTPUT_PATH = Path("data/endgame_history.csv")

MODE_KEYS = {
    "Memory of Chaos": "moc",
    "Apocalyptic Shadow": "apoc",
    "Pure Fiction": "pf",
    "Anomaly Arbitration": "aa",  # covers both "Anomaly Arbitration" and "...: King"
}

CSV_HEADER = [
    "Date", "Version", "Mode", "Side", "Season ID", "Boss", "Boss Icon",
    "Member 1", "Member 1 Icon", "Member 2", "Member 2 Icon",
    "Member 3", "Member 3 Icon", "Member 4", "Member 4 Icon", "Score",
]

ELITE_ENEMIES_LABEL = "elite enemies"


async def build_endgame_history_csv(
    gs_client: GoogleSheetsClient,
    nanoka_characters: NanokaCharacterData,
    genshin_client: genshin.Client,
    uid: int,
    output_path: Path = OUTPUT_PATH,
) -> None:
    rows = gs_client.get_all_rows()[1:]
    reverse_short_names = {short: full for full, short in HSR_SHORT_NAMES.items()}

    apoc_anchor = await _apoc_anchor(genshin_client, uid)
    pf_anchor = await _pf_anchor(genshin_client, uid)

    csv_rows = []
    async with await BossLookup.create() as lookup:
        for row in rows:
            date_str, patch, mode, side = row[DATE_COL], row[VERSION_COL], row[MODE_COL], row[SIDE_COL]
            manual_boss = row[NOTES_COL]
            members = row[NOTES_COL + 1 : SCORE_COL]
            score = row[SCORE_COL]

            mode_key = next((key for prefix, key in MODE_KEYS.items() if mode.startswith(prefix)), None)
            if mode_key is None:
                continue

            try:
                row_date = datetime.strptime(date_str, "%m/%d/%Y").date()
            except ValueError:
                logger.warning("Skipping unparseable date %r in endgame history export", date_str)
                continue

            try:
                resolved = await lookup.resolve(
                    mode_key, patch, side, row_date, apoc_anchor=apoc_anchor, pf_anchor=pf_anchor
                )
            except Exception:
                logger.warning("Boss lookup failed for %s row on %s", mode, date_str, exc_info=True)
                continue

            boss_name = manual_boss.strip()
            boss_icon = ""
            if boss_name:
                if boss_name.lower() == ELITE_ENEMIES_LABEL:
                    boss_icon = resolved.elite_icon_url or ""
                else:
                    boss_icon = await lookup.find_icon_by_name(boss_name) or ""

            member_cells = []
            for raw_member_name in members:
                member_name = str(raw_member_name)
                character_id = None
                if member_name:
                    full_name = reverse_short_names.get(member_name, member_name)
                    character_id = nanoka_characters.find_id_by_name(full_name)
                member_cells.append(member_name)
                member_cells.append(character_icon_url(character_id) if character_id else "")

            csv_rows.append(
                [date_str, patch, mode, side, resolved.season_id, boss_name, boss_icon]
                + member_cells
                + [score]
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)
        writer.writerows(csv_rows)

    logger.info("Wrote %d rows to %s", len(csv_rows), output_path)


async def _apoc_anchor(genshin_client: genshin.Client, uid: int) -> tuple[int, date] | None:
    challenge = await genshin_client.get_starrail_apc_shadow(uid=uid)
    if not challenge.has_data or not challenge.seasons:
        return None
    season = challenge.seasons[0]
    return season.id, season.begin_time.datetime.date()


async def _pf_anchor(genshin_client: genshin.Client, uid: int) -> tuple[int, date] | None:
    challenge = await genshin_client.get_starrail_pure_fiction(uid=uid)
    if not challenge.has_data or not challenge.seasons:
        return None
    season = challenge.seasons[0]
    return season.id, season.begin_time.datetime.date()
