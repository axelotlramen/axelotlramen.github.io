import typing

import httpx

from scripts.constants import HSR_PATHS


class NanokaClient:
    """Client for Nanoka, a third-party HSR character metadata site, used for ID -> name/path lookup."""

    BASE_URL = "https://static.nanoka.cc"

    DEFAULT_HEADERS = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8",
        "cache-control": "no-cache",
        "origin": "https://hsr.nanoka.cc",
        "pragma": "no-cache",
        "referer": "https://hsr.nanoka.cc/",
        "user-agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0"
        ),
    }

    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL, headers=self.DEFAULT_HEADERS, timeout=30.0
        )
        self._latest_version: str | None = None

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self) -> "NanokaClient":
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.close()

    async def get_latest_version(self) -> str:
        """Current HSR data version Nanoka has. Cached per client instance."""
        if self._latest_version is None:
            response = await self.client.get("/manifest.json")
            response.raise_for_status()
            self._latest_version = str(response.json()["hsr"]["latest"])
        return self._latest_version

    async def get_characters(self) -> "NanokaCharacterData":
        version = await self.get_latest_version()
        response = await self.client.get(f"/hsr/{version}/character.json")
        response.raise_for_status()
        return NanokaCharacterData(response.json())

    async def get_moc_floor_bosses(self, floor_id: int, season_id: int) -> dict[str, str | None]:
        """Boss name for each side of one MoC floor, including the Starward-mode third
        side when the floor has one (a separate entry in the same list whose `pre_id`
        points back at floor_id).

        One request for the season's floor list (`en/maze/{season_id}.json`), plus one
        request per distinct boss monster id (deduped) to resolve names - a handful of
        requests total, never more than 4.
        """
        empty: dict[str, str | None] = {"first_half": None, "second_half": None, "third_half": None}
        version = await self.get_latest_version()

        floors_response = await self.client.get(f"/hsr/{version}/en/maze/{season_id}.json")
        if floors_response.status_code == 404:
            return empty
        floors_response.raise_for_status()
        floors = floors_response.json()

        floor = next((f for f in floors if f.get("id") == floor_id), None)
        if floor is None:
            return empty

        starward = next((f for f in floors if f.get("pre_id") == floor_id), None)

        monster_ids = {
            "first_half": _last_monster_id(floor.get("event_id_list1")),
            "second_half": _last_monster_id(floor.get("event_id_list2")),
            "third_half": _last_monster_id(starward.get("event_id_list")) if starward else None,
        }

        return await self._resolve_monster_names(monster_ids, version)

    async def get_apoc_boss_names(self, season_id: int) -> dict[str, str | None]:
        """Boss name for each side of one Apocalyptic Shadow season, including the
        Starward-mode third side (a separate entry in the same list identified by `pre_id`,
        same pattern as MoC). Fallback only - HoYoLab's own season.upper_boss/lower_boss/
        starward_boss are already exact; this just fills gaps.

        Safe to use any difficulty tier Nanoka has: boss ids are 9 digits where the last
        2 encode the tier (e.g. 302401301..302401304), and the monster database only
        indexes the base 7-digit id, so every tier resolves to the same name.
        """
        empty: dict[str, str | None] = {"upper": None, "lower": None, "starward": None}
        version = await self.get_latest_version()

        response = await self.client.get(f"/hsr/{version}/en/boss/{season_id}.json")
        if response.status_code == 404:
            return empty
        response.raise_for_status()
        levels = response.json().get("level") or []

        tier = next((lvl for lvl in levels if "boss_monster_id1" in lvl), None)
        starward = next((lvl for lvl in levels if "pre_id" in lvl), None)

        monster_ids = {
            "upper": tier.get("boss_monster_id1") if tier else None,
            "lower": tier.get("boss_monster_id2") if tier else None,
            "starward": starward.get("boss_monster_id") if starward else None,
        }

        return await self._resolve_monster_names(monster_ids, version)

    async def get_pf_boss_names(self, season_id: int) -> dict[str, str | None]:
        """Boss name for each side of one Pure Fiction season, including the Starward-mode
        third side (same `pre_id` pattern as MoC/APOC). Fallback only - genshin.py has no
        enemy-identity field at all for PF, so this is the sole source when it's used.

        Unlike APOC, PF's difficulty tiers use genuinely different enemies rather than
        scaled variants of the same one, so there's no id trick to sidestep picking a
        tier - this takes the highest tier Nanoka has as a best-effort guess at what the
        account actually fought.
        """
        empty: dict[str, str | None] = {"first_half": None, "second_half": None, "third_half": None}
        version = await self.get_latest_version()

        response = await self.client.get(f"/hsr/{version}/en/story/{season_id}.json")
        if response.status_code == 404:
            return empty
        response.raise_for_status()
        levels = response.json().get("level") or []

        tiers = [lvl for lvl in levels if "npc_monster_id_list1" in lvl]
        tier = tiers[-1] if tiers else None
        starward = next((lvl for lvl in levels if "pre_id" in lvl), None)

        monster_ids = {
            "first_half": _first_or_none(tier.get("npc_monster_id_list1")) if tier else None,
            "second_half": _first_or_none(tier.get("npc_monster_id_list2")) if tier else None,
            "third_half": _first_or_none(starward.get("npc_monster_id_list")) if starward else None,
        }

        return await self._resolve_monster_names(monster_ids, version)

    async def get_aa_boss_names(self, season_id: int) -> dict[int, str | None]:
        """Boss/mini-boss name for each entry in one Anomaly Arbitration season, keyed by
        the same id genshin.py's AnomalyBossInfo/AnomalyMiniBossInfo expose. Fallback only -
        genshin.py's own per-fight names are already exact; this just fills gaps.

        One request for the season's peak data (`en/peak/{season_id}.json`), plus one
        request per distinct boss monster id (deduped) to resolve names.
        """
        version = await self.get_latest_version()

        response = await self.client.get(f"/hsr/{version}/en/peak/{season_id}.json")
        if response.status_code == 404:
            return {}
        response.raise_for_status()
        data = response.json()

        entries = list(data.get("pre_level") or [])
        if data.get("boss_level"):
            entries.append(data["boss_level"])

        monster_ids = {entry["id"]: _last_monster_id(entry.get("event_id_list")) for entry in entries}

        return await self._resolve_monster_names(monster_ids, version)

    async def _resolve_monster_names(
        self, monster_ids: dict[typing.Any, int | None], version: str
    ) -> dict[typing.Any, str | None]:
        """Resolve a batch of {key: monster_id} into {key: monster_name}, deduping requests."""
        truncated_ids = {
            key: _truncate_monster_id(mid) if mid is not None else None
            for key, mid in monster_ids.items()
        }

        names: dict[int, str] = {}
        for monster_id in {mid for mid in truncated_ids.values() if mid is not None}:
            response = await self.client.get(f"/hsr/{version}/en/monster/{monster_id}.json")
            if response.status_code == 404:
                continue
            response.raise_for_status()
            names[monster_id] = response.json().get("name")

        return {key: names.get(mid) if mid is not None else None for key, mid in truncated_ids.items()}


def _last_monster_id(event_id_list) -> int | None:
    """The last monster in a stage's final wave - usually the floor's boss."""
    if not event_id_list:
        return None

    monster_list = event_id_list[0].get("monster_list") or []
    if not monster_list:
        return None

    last_wave = monster_list[-1]
    monster_values = list(last_wave.values())
    return monster_values[-1] if monster_values else None


def _first_or_none(values: list[int] | None) -> int | None:
    return values[0] if values else None


def _truncate_monster_id(monster_id: int) -> int:
    """IDs above 7 digits encode a difficulty/variant suffix the monster database doesn't
    index separately - matches hakushin-py's own truncation rule for the same data."""
    return int(str(monster_id)[:7]) if monster_id > 9999999 else monster_id


class NanokaCharacterData:
    SPECIAL_NAME_RULE = {
        "{NICKNAME}": lambda self, character_id: (
            f"{self.get_path(character_id)} Trailblazer"
        ),
        "March 7th": lambda self, character_id: (
            f"{self.get_path(character_id)} March 7th"
        ),
    }

    def __init__(self, data: dict):
        self.data = data

    def get_character(self, character_id: str | int) -> dict | None:
        return self.data.get(str(character_id))

    def get_name(self, character_id: str | int) -> str | None:
        character = self.get_character(character_id)
        if character is None:
            return None

        name = character.get("en")
        rule = self.SPECIAL_NAME_RULE.get(str(name))
        if rule:
            return rule(self, character_id)

        return name

    def get_path(self, character_id: str | int) -> str | None:
        character = self.get_character(character_id)
        if character is None:
            return None

        return HSR_PATHS.get(character.get("baseType", ""), "")

    def get_all_characters(self) -> dict:
        return self.data

    def __len__(self) -> int:
        return len(self.data)
