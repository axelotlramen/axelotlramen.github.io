import typing

import genshin

from scripts.constants import HSR_SHORT_NAMES
from scripts.sheets.enums import ChallengeMode, HSRMode, SheetRow
from scripts.sheets.nanoka import NanokaClient, NanokaCharacterData
from scripts.sheets.sheets_client import GoogleSheetsClient, UpsertResult
from scripts.sheets.version import VersionResolver


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
        nanoka_characters = await NanokaClient().get_characters()
        return cls(genshin_client, uid, gs_client, version_resolver, nanoka_characters)

    async def build_rows(self, mode: ChallengeMode) -> list[SheetRow]:
        """Fetch one mode and transform it into sheet rows. No Sheets I/O."""
        match mode:
            case ChallengeMode.APOC:
                challenge = await self.genshin_client.get_starrail_apc_shadow(uid=self.uid)
                if not challenge.has_data or not challenge.floors:
                    return []
                return self._build_rows(HSRMode.APOC, challenge)

            case ChallengeMode.PF:
                challenge = await self.genshin_client.get_starrail_pure_fiction(uid=self.uid)
                if not challenge.has_data or not challenge.floors:
                    return []
                return self._build_rows(HSRMode.PF, challenge)

            case ChallengeMode.MOC:
                challenge = await self.genshin_client.get_starrail_challenge(uid=self.uid)
                if not challenge.has_data or not challenge.floors:
                    return []
                # MoC has no computed score - _preserve_manual_scores fills it in later.
                return self._build_rows(HSRMode.MOC, challenge, score_of=lambda _: "")

            case ChallengeMode.AA:
                arbitration = await self.genshin_client.get_anomaly_arbitration(uid=self.uid)
                if not arbitration.records or not arbitration.records[0].has_data:
                    return []
                return self._build_aa_rows(arbitration.records[0])

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
                )
            )

        return rows

    def _floor_nodes(self, floor) -> list[tuple[str, typing.Any]]:
        return [
            ("Node 1", floor.node_1),
            ("Node 2", floor.node_2),
            ("Node 3", floor.node_3),
        ]

    def _build_aa_rows(self, record) -> list[SheetRow]:
        date_str = record.season.end_time.datetime.strftime("%m/%d/%Y")
        version = record.season.game_version

        rows = []
        for i, mini_boss_record in enumerate(record.mini_boss_records, start=1):
            rows.append(
                self._build_row(
                    date_str=date_str,
                    version=version,
                    mode=HSRMode.AA,
                    side_name=f"Knight {i}",
                    avatars=mini_boss_record.characters,
                    score=mini_boss_record.cycles_used,
                )
            )

        if record.boss_record is not None:
            rows.append(
                self._build_row(
                    date_str=date_str,
                    version=version,
                    mode=HSRMode.AA_KING,
                    side_name="",
                    avatars=record.boss_record.characters,
                    score=record.boss_record.cycles_used,
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
    ) -> SheetRow:
        return [
            date_str,
            version,
            mode.value,
            side_name,
            "",
            *self._get_avatar_names(avatars),
            score,
        ]

    def _get_avatar_names(self, avatars) -> list[str]:
        result = []
        for avatar in avatars:
            name = self.nanoka_characters.get_name(avatar.id)
            result.append(HSR_SHORT_NAMES.get(name, name) if name is not None else name)

        return result
