"""Independent boss/mini-boss resolution for HSR endgame history.

Not wired into the daily sheet-writing pipeline (scripts.sheets.writer) - the Sheet's own
Boss column stays purely manual. This is used by the endgame history CSV export and by
the personal preview-generator tool in codebase_reviews/, both of which need a boss name
(and icon) resolved the same way regardless of whatever text a human has typed into the
sheet, so it can be reliably filtered/iconified.

MoC and Anomaly Arbitration seasons map exactly to a game version via Nanoka's own
en/maze/version.json and en/peak/version.json. Apocalyptic Shadow and Pure Fiction have no
such mapping anywhere on Nanoka, so their season id is estimated from a known (season,
date) anchor plus an assumed ~6-week rotation cadence - always "guessed", never exact.

Every mode resolves the same way: a stage's enemies are walked from last to first (see
_find_boss_monster), and the first one ranked BigBoss or LittleBoss wins - a fixed wave
position isn't always the actual boss (e.g. an AA Knight fight can end on a MinionLv2
trash mob). If nothing in the stage reaches boss rank, the name falls back to a synthetic
"Elite Enemies". APOC/PF also expose an explicit boss-id field directly, but everything
goes through this same rank-walk instead, for one consistent algorithm across all four
modes rather than two different mechanisms.
"""

import asyncio
from dataclasses import dataclass
from datetime import date

import httpx

NANOKA_BASE_URL = "https://static.nanoka.cc"
ASSET_BASE_URL = "https://static.nanoka.cc/assets/hsr"

APOC_STEP_DAYS = 42
PF_STEP_DAYS = 42
APOC_ID_RANGE = (3001, 3020)
PF_ID_RANGE = (2001, 2026)

SIDE_KEYS = ("Node 1", "Node 2", "Node 3")


@dataclass
class ResolvedBoss:
    name: str | None
    icon_url: str | None
    confidence: str  # "exact" or "guessed"
    season_id: int | None = None
    # A representative Elite-rank icon from the stage's last wave, found as a side effect
    # of the same search - used when a manually-verified sheet entry is literally "Elite
    # Enemies" and there's no single named boss to point an icon at.
    elite_icon_url: str | None = None


class BossLookup:
    """Resolves the top-floor/top-tier boss for a historical HSR endgame row."""

    def __init__(self, client: httpx.AsyncClient, version: str):
        self.client = client
        self.version = version
        self._maze_version_map: dict | None = None
        self._peak_version_map: dict | None = None
        self._monster_icons: dict[str, str | None] | None = None
        self._season_cache: dict[tuple, dict] = {}

    @classmethod
    async def create(cls) -> "BossLookup":
        client = httpx.AsyncClient(base_url=NANOKA_BASE_URL, timeout=30.0)
        manifest = await _get_json(client, "/manifest.json")
        return cls(client, str(manifest["hsr"]["latest"]))

    async def close(self) -> None:
        await self.client.aclose()

    async def __aenter__(self) -> "BossLookup":
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.close()

    async def resolve(
        self,
        mode: str,
        patch: str,
        side: str,
        row_date: date,
        apoc_anchor: tuple[int, date] | None = None,
        pf_anchor: tuple[int, date] | None = None,
    ) -> ResolvedBoss:
        """mode: 'moc' | 'apoc' | 'pf' | 'aa'. side: 'Node 1'/'Node 2'/'Node 3' for
        moc/apoc/pf, 'Knight 1'/'Knight 2'/'Knight 3'/'' (king) for aa."""
        if mode == "moc":
            season_id = await self._version_mapped_season(await self._maze_versions(), patch)
            if season_id is None:
                return ResolvedBoss(None, None, "exact")
            bosses = await self._moc_bosses(season_id)
            return self._to_resolved(bosses.get(side), "exact", season_id)

        if mode == "aa":
            season_id = await self._version_mapped_season(await self._peak_versions(), patch)
            if season_id is None:
                return ResolvedBoss(None, None, "exact")
            bosses = await self._aa_bosses(season_id)
            return self._to_resolved(bosses.get(side), "exact", season_id)

        if mode == "apoc":
            if apoc_anchor is None:
                raise ValueError("apoc_anchor is required to resolve an Apocalyptic Shadow row")
            season_id = _estimate_season_id(*apoc_anchor, row_date, APOC_STEP_DAYS, APOC_ID_RANGE)
            bosses = await self._apoc_bosses(season_id)
            return self._to_resolved(bosses.get(side), "guessed", season_id)

        if mode == "pf":
            if pf_anchor is None:
                raise ValueError("pf_anchor is required to resolve a Pure Fiction row")
            season_id = _estimate_season_id(*pf_anchor, row_date, PF_STEP_DAYS, PF_ID_RANGE)
            bosses = await self._pf_bosses(season_id)
            return self._to_resolved(bosses.get(side), "guessed", season_id)

        raise ValueError(f"Unknown mode: {mode}")

    async def _version_mapped_season(self, version_map: dict, patch: str) -> int | None:
        season_ids = version_map.get(patch)
        return season_ids[0] if season_ids else None

    async def _maze_versions(self) -> dict:
        version_map = self._maze_version_map
        if version_map is None:
            version_map = await _get_json(self.client, f"/hsr/{self.version}/en/maze/version.json")
            self._maze_version_map = version_map
        return version_map

    async def _peak_versions(self) -> dict:
        version_map = self._peak_version_map
        if version_map is None:
            version_map = await _get_json(self.client, f"/hsr/{self.version}/en/peak/version.json")
            self._peak_version_map = version_map
        return version_map

    async def find_icon_by_name(self, name: str) -> str | None:
        """Icon for a monster by its exact display name (case-insensitive), built from
        Nanoka's bulk monster list. Trusts a manually-verified Boss name directly rather
        than re-guessing which enemy in a wave was the intended boss."""
        index = await self._monster_icon_index()
        return index.get(name.strip().lower())

    async def _monster_icon_index(self) -> dict[str, str | None]:
        icons = self._monster_icons
        if icons is None:
            data = await _get_json(self.client, f"/hsr/{self.version}/monster.json")
            icons = {
                entry["en"].strip().lower(): _monster_icon_url(entry.get("icon"))
                for entry in data.values()
                if entry.get("en")
            }
            self._monster_icons = icons
        return icons

    def _to_resolved(self, entry: tuple | None, confidence: str, season_id: int) -> ResolvedBoss:
        if entry is None:
            return ResolvedBoss(None, None, confidence, season_id)
        name, icon_url, elite_icon_url = entry
        return ResolvedBoss(name, icon_url, confidence, season_id, elite_icon_url)

    async def _moc_bosses(self, season_id: int) -> dict:
        cache_key = ("moc", season_id)
        if cache_key not in self._season_cache:
            floors = await _get_optional_json(self.client, f"/hsr/{self.version}/en/maze/{season_id}.json")
            if not floors:
                self._season_cache[cache_key] = {}
            else:
                real_floors = [f for f in floors if "pre_id" not in f]
                top = max(real_floors, key=lambda f: f["id"]) if real_floors else None
                starward = next((f for f in floors if top and f.get("pre_id") == top["id"]), None)

                node1, node2, node3 = await asyncio.gather(
                    self._find_boss_monster(top.get("event_id_list1") if top else None),
                    self._find_boss_monster(top.get("event_id_list2") if top else None),
                    self._find_boss_monster(starward.get("event_id_list") if starward else None),
                )
                self._season_cache[cache_key] = {"Node 1": node1, "Node 2": node2, "Node 3": node3}
        return self._season_cache[cache_key]

    async def _aa_bosses(self, season_id: int) -> dict:
        cache_key = ("aa", season_id)
        if cache_key not in self._season_cache:
            data = await _get_optional_json(self.client, f"/hsr/{self.version}/en/peak/{season_id}.json")
            if not data:
                self._season_cache[cache_key] = {}
            else:
                entries = list(data.get("pre_level") or [])
                boss_level = data.get("boss_level")

                keys = [f"Knight {i}" for i in range(1, len(entries) + 1)]
                tasks = [self._find_boss_monster(entry.get("event_id_list")) for entry in entries]
                if boss_level:
                    keys.append("")
                    tasks.append(self._find_boss_monster(boss_level.get("event_id_list")))

                results = await asyncio.gather(*tasks)
                self._season_cache[cache_key] = dict(zip(keys, results))
        return self._season_cache[cache_key]

    async def _find_boss_monster(
        self, event_id_list
    ) -> tuple[str, str | None, str | None] | None:
        """Walk a stage's enemies from last to first, checking each one's rank, and use
        the first BigBoss or LittleBoss found. Falls back to a synthetic "Elite Enemies"
        name (no icon of its own) if the stage has enemies but none of them reach boss
        rank. Also returns a representative Elite-rank icon from the last wave
        specifically, found as a side effect of the same walk. Returns None only when
        there's no stage at all (e.g. this floor has no third side)."""
        if not event_id_list:
            return None

        monster_list = event_id_list[0].get("monster_list") or []
        if not monster_list:
            return None

        last_wave_ids = {value for value in monster_list[-1].values() if isinstance(value, int)}
        all_ids = [value for wave in monster_list for value in wave.values() if isinstance(value, int)]

        boss_result: tuple[str, str | None] | None = None
        elite_icon: str | None = None

        for monster_id in reversed(all_ids):
            data = await _get_optional_json(
                self.client, f"/hsr/{self.version}/en/monster/{_truncate_monster_id(monster_id)}.json"
            )
            if not data:
                continue

            rank = data.get("rank")
            if boss_result is None and rank in ("BigBoss", "LittleBoss") and data.get("name"):
                boss_result = (data["name"], _monster_icon_url(data.get("image_path")))
            elif elite_icon is None and rank == "Elite" and monster_id in last_wave_ids:
                elite_icon = _monster_icon_url(data.get("image_path"))

        if boss_result:
            return boss_result[0], boss_result[1], elite_icon
        return "Elite Enemies", None, elite_icon

    async def _apoc_bosses(self, season_id: int) -> dict:
        cache_key = ("apoc", season_id)
        if cache_key not in self._season_cache:
            data = await _get_optional_json(self.client, f"/hsr/{self.version}/en/boss/{season_id}.json")
            if not data:
                self._season_cache[cache_key] = {}
            else:
                levels = data.get("level") or []
                tier = next((lvl for lvl in levels if "boss_monster_id1" in lvl), None)
                starward = next((lvl for lvl in levels if "pre_id" in lvl), None)

                node1, node2, node3 = await asyncio.gather(
                    self._find_boss_monster(tier.get("event_id_list1") if tier else None),
                    self._find_boss_monster(tier.get("event_id_list2") if tier else None),
                    self._find_boss_monster(starward.get("event_id_list") if starward else None),
                )
                self._season_cache[cache_key] = {"Node 1": node1, "Node 2": node2, "Node 3": node3}
        return self._season_cache[cache_key]

    async def _pf_bosses(self, season_id: int) -> dict:
        cache_key = ("pf", season_id)
        if cache_key not in self._season_cache:
            data = await _get_optional_json(self.client, f"/hsr/{self.version}/en/story/{season_id}.json")
            if not data:
                self._season_cache[cache_key] = {}
            else:
                levels = data.get("level") or []
                # PF's tiers have genuinely different enemies (unlike APOC's, which are just
                # scaled variants of the same one) - the highest tier is the best-effort
                # guess at what the account actually fought.
                tiers = [lvl for lvl in levels if "npc_monster_id_list1" in lvl]
                tier = tiers[-1] if tiers else None
                starward = next((lvl for lvl in levels if "pre_id" in lvl), None)

                node1, node2, node3 = await asyncio.gather(
                    self._find_boss_monster(tier.get("event_id_list1") if tier else None),
                    self._find_boss_monster(tier.get("event_id_list2") if tier else None),
                    self._find_boss_monster(starward.get("event_id_list") if starward else None),
                )
                self._season_cache[cache_key] = {"Node 1": node1, "Node 2": node2, "Node 3": node3}
        return self._season_cache[cache_key]


RETRY_COUNT = 3


async def _get_json(client: httpx.AsyncClient, path: str):
    for attempt in range(RETRY_COUNT):
        try:
            response = await client.get(path)
            response.raise_for_status()
            return response.json()
        except httpx.TransportError:
            if attempt == RETRY_COUNT - 1:
                raise
            await asyncio.sleep(1)
    raise AssertionError("unreachable")  # loop above always returns or raises


async def _get_optional_json(client: httpx.AsyncClient, path: str):
    for attempt in range(RETRY_COUNT):
        try:
            response = await client.get(path)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except httpx.TransportError:
            if attempt == RETRY_COUNT - 1:
                raise
            await asyncio.sleep(1)
    raise AssertionError("unreachable")  # loop above always returns or raises


def _truncate_monster_id(monster_id: int) -> int:
    """IDs above 7 digits encode a difficulty/variant suffix the monster database doesn't
    index separately (matches hakushin-py's own rule for the same data)."""
    return int(str(monster_id)[:7]) if monster_id > 9999999 else monster_id


def _monster_icon_url(image_path: str | None) -> str | None:
    if not image_path:
        return None
    basename = image_path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    return f"{ASSET_BASE_URL}/monsterfigure/{basename}.webp"


def _estimate_season_id(
    anchor_id: int, anchor_date: date, row_date: date, step_days: int, id_range: tuple[int, int]
) -> int:
    days_diff = (anchor_date - row_date).days
    steps = round(days_diff / step_days)
    estimated = anchor_id - steps
    return max(id_range[0], min(id_range[1], estimated))


def character_icon_url(character_id: str | int) -> str:
    """Same convention already used by the frontend (script.js) for character icons."""
    return f"https://stardb.gg/api/static/StarRailResWebp/icon/character/{character_id}.webp"
