import logging
import typing

import genshin

from scripts.constants import HSR_SHORT_NAMES
from scripts.sheets.enums import ChallengeMode, HSRMode, SheetRow
from scripts.sheets.nanoka import NanokaClient, NanokaCharacterData
from scripts.sheets.sheets_client import NOTES_COL, SIDE_COL, GoogleSheetsClient, UpsertResult
from scripts.sheets.version import VersionResolver

logger = logging.getLogger("sheet_writer")


class SheetWriter:
    """Fetches HSR challenge-mode data and writes it into the endgame Google Sheet."""

    def __init__(
        self,
        genshin_client: genshin.Client,
        uid: int,
        gs_client: GoogleSheetsClient,
        version_resolver: VersionResolver,
        nanoka_characters: NanokaCharacterData,
    ) -> None:
        self.genshin_client = genshin_client
        self.uid = uid
        self.gs_client = gs_client
        self.version_resolver = version_resolver
        self.nanoka_characters = nanoka_characters

    @classmethod
    async def create(
        cls,
        genshin_client: genshin.Client,
        uid: int,
        gs_client: GoogleSheetsClient,
        version_resolver: VersionResolver,
    ) -> "SheetWriter":
        async with NanokaClient() as nanoka:
            nanoka_characters = await nanoka.get_characters()
        return cls(genshin_client, uid, gs_client, version_resolver, nanoka_characters)

    async def build_rows(self, mode: ChallengeMode) -> list[SheetRow]:
        """Fetch one mode and transform it into sheet rows. No Sheets I/O."""
        match mode:
            case ChallengeMode.APOC:
                challenge = await self.genshin_client.get_starrail_apc_shadow(uid=self.uid)
                if not challenge.has_data or not challenge.floors:
                    return []
                # HoYoLab already gives a named boss per side; Nanoka only backstops it.
                season = challenge.seasons[0]
                fallback = await self._get_apoc_fallback_names(season.id)
                boss_by_side = {
                    "Node 1": (season.upper_boss.name if season.upper_boss else "") or fallback.get("upper") or "",
                    "Node 2": (season.lower_boss.name if season.lower_boss else "") or fallback.get("lower") or "",
                    "Node 3": (
                        (season.starward_boss.name if season.starward_boss else "")
                        or fallback.get("starward")
                        or ""
                    ),
                }
                return self._build_rows(
                    HSRMode.APOC, challenge, notes_of=lambda side: boss_by_side.get(side, "")
                )

            case ChallengeMode.PF:
                challenge = await self.genshin_client.get_starrail_pure_fiction(uid=self.uid)
                if not challenge.has_data or not challenge.floors:
                    return []
                # genshin.py has no enemy identity for PF at all - Nanoka is the only source,
                # falling back to the season's theme title if a side's lookup comes up empty.
                season = challenge.seasons[0]
                boss_by_side = await self._get_pf_boss_notes(season.id, season.name)
                return self._build_rows(HSRMode.PF, challenge, notes_of=lambda side: boss_by_side.get(side, ""))

            case ChallengeMode.MOC:
                challenge = await self.genshin_client.get_starrail_challenge(uid=self.uid)
                if not challenge.has_data or not challenge.floors:
                    return []
                # MoC has no computed score - _preserve_manual_entries fills it in later.
                rows = self._build_rows(HSRMode.MOC, challenge, score_of=lambda _: "")
                await self._fill_moc_boss_notes(rows, challenge.floors[0], challenge.seasons[0].id)
                return rows

            case ChallengeMode.AA:
                arbitration = await self.genshin_client.get_anomaly_arbitration(uid=self.uid)
                if not arbitration.records or not arbitration.records[0].has_data:
                    return []
                record = arbitration.records[0]
                fallback_names = await self._get_aa_fallback_names(record.season.id)
                return self._build_aa_rows(record, fallback_names)

            case _:
                raise ValueError(f"Unknown challenge mode: {mode}")

    async def write_mode(self, mode: ChallengeMode) -> UpsertResult:
        rows = await self.build_rows(mode)
        return self.gs_client.upsert_rows(rows)

    def _build_rows(
        self,
        mode: HSRMode,
        challenge,
        score_of=lambda node: node.score,
        notes_of=lambda _: "",
    ) -> list[SheetRow]:
        floor = challenge.floors[0]

        date = challenge.seasons[0].begin_time.datetime.date()
        date_str = date.strftime("%m/%d/%Y")
        version = self.version_resolver.resolve(date)

        rows = []
        for side_name, node in self._floor_nodes(floor):
            if node is None:
                continue

            rows.append(
                self._build_row(
                    date_str=date_str,
                    version=version,
                    mode=mode,
                    side_name=side_name,
                    avatars=node.avatars,
                    score=score_of(node),
                    notes=notes_of(side_name),
                )
            )

        return rows

    async def _fill_moc_boss_notes(self, rows: list[SheetRow], floor, season_id: int) -> None:
        """Best-effort: look up this floor's boss names via Nanoka and fill them into the
        Notes column. Leaves rows untouched on any failure - HoYoLab's own MoC data never
        includes enemy identity, so this is purely a nice-to-have on top of it. A blank
        Notes value here just falls back to whatever a human already typed in, via
        _preserve_manual_entries in sheets_client.py."""
        try:
            async with NanokaClient() as nanoka:
                bosses = await nanoka.get_moc_floor_bosses(floor_id=floor.id, season_id=season_id)
        except Exception:
            logger.warning("Nanoka MoC boss lookup failed - leaving Notes blank", exc_info=True)
            return

        boss_by_side = {
            "Node 1": bosses.get("first_half"),
            "Node 2": bosses.get("second_half"),
            "Node 3": bosses.get("third_half"),
        }
        for row in rows:
            boss = boss_by_side.get(row[SIDE_COL])
            if boss:
                row[NOTES_COL] = boss

    def _floor_nodes(self, floor) -> list[tuple[str, typing.Any]]:
        return [
            ("Node 1", floor.node_1),
            ("Node 2", floor.node_2),
            ("Node 3", floor.node_3),
        ]

    async def _get_apoc_fallback_names(self, season_id: int) -> dict[str, str | None]:
        """Best-effort backstop for APOC boss names, looked up via Nanoka. Never overrides
        HoYoLab's own season.upper_boss/lower_boss/starward_boss names."""
        try:
            async with NanokaClient() as nanoka:
                return await nanoka.get_apoc_boss_names(season_id)
        except Exception:
            logger.warning("Nanoka APOC boss lookup failed - leaving fallback empty", exc_info=True)
            return {}

    async def _get_pf_boss_notes(self, season_id: int, fallback_theme: str) -> dict[str, str]:
        """Per-side boss name for PF via Nanoka - the sole source, since genshin.py has no
        enemy-identity field for PF. Falls back to the season's theme title per side if the
        lookup fails or doesn't have a name for that side."""
        try:
            async with NanokaClient() as nanoka:
                bosses = await nanoka.get_pf_boss_names(season_id)
        except Exception:
            logger.warning("Nanoka PF boss lookup failed - falling back to theme title", exc_info=True)
            bosses = {}

        return {
            "Node 1": bosses.get("first_half") or fallback_theme,
            "Node 2": bosses.get("second_half") or fallback_theme,
            "Node 3": bosses.get("third_half") or fallback_theme,
        }

    async def _get_aa_fallback_names(self, season_id: int) -> dict[int, str | None]:
        """Best-effort backstop for AA rows genshin.py couldn't name (e.g. an unmapped
        mini-boss id) - looked up via Nanoka. Never overrides a real per-fight name."""
        try:
            async with NanokaClient() as nanoka:
                return await nanoka.get_aa_boss_names(season_id)
        except Exception:
            logger.warning("Nanoka AA boss lookup failed - leaving fallback empty", exc_info=True)
            return {}

    def _build_aa_rows(
        self, record, fallback_names: dict[int, str | None] | None = None
    ) -> list[SheetRow]:
        fallback_names = fallback_names or {}
        date_str = record.season.end_time.datetime.strftime("%m/%d/%Y")
        version = record.season.game_version

        # record.mini_bosses are this cycle's mini-boss definitions (names); mini_boss_records
        # are the player's fights against them - matched here by id, same order in practice.
        mini_boss_names = {mini_boss.id: mini_boss.name for mini_boss in record.mini_bosses}

        rows = []
        for i, mini_boss_record in enumerate(record.mini_boss_records, start=1):
            notes = mini_boss_names.get(mini_boss_record.id) or fallback_names.get(mini_boss_record.id) or ""
            rows.append(
                self._build_row(
                    date_str=date_str,
                    version=version,
                    mode=HSRMode.AA,
                    side_name=f"Knight {i}",
                    avatars=mini_boss_record.characters,
                    score=mini_boss_record.cycles_used,
                    notes=notes,
                )
            )

        if record.boss_record is not None:
            notes = record.boss.name or fallback_names.get(record.boss.id) or ""
            rows.append(
                self._build_row(
                    date_str=date_str,
                    version=version,
                    mode=HSRMode.AA_KING,
                    side_name="",
                    avatars=record.boss_record.characters,
                    score=record.boss_record.cycles_used,
                    notes=notes,
                )
            )

        return rows

    def _build_row(
        self,
        date_str: str,
        version: str,
        mode: HSRMode,
        side_name: str,
        avatars,
        score: int | str,
        notes: str = "",
    ) -> SheetRow:
        return [
            date_str,
            version,
            mode.value,
            side_name,
            notes,
            *self._get_avatar_names(avatars),
            score,
        ]

    def _get_avatar_names(self, avatars) -> list[str]:
        result = []
        for avatar in avatars:
            name = self.nanoka_characters.get_name(avatar.id)
            result.append(HSR_SHORT_NAMES.get(name, name) if name is not None else name)

        return result
