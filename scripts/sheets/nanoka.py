import typing

import httpx

from scripts.constants import HSR_PATHS


class NanokaClient:
    """Client for Nanoka, a third-party HSR character metadata site, used for ID -> name/path lookup."""

    BASE_URL = "https://static.nanoka.cc"

    def __init__(self):
        self.client = httpx.AsyncClient(base_url=self.BASE_URL, timeout=30.0)
        self._latest_version: str | None = None

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self) -> "NanokaClient":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: typing.Any,
    ) -> None:
        await self.close()

    async def get_latest_version(self) -> str:
        """Current HSR data version Nanoka has. Cached per client instance."""
        if self._latest_version is None:
            data = await self._get_json("/manifest.json")
            self._latest_version = str(data["hsr"]["latest"])
        return self._latest_version

    async def get_characters(self) -> "NanokaCharacterData":
        version = await self.get_latest_version()
        data = await self._get_json(f"/hsr/{version}/character.json")
        return NanokaCharacterData(data)

    async def _get_json(self, path: str) -> typing.Any:
        response = await self.client.get(path)
        response.raise_for_status()
        return response.json()


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
        self._name_index: dict[str, str] | None = None

    def get_character(self, character_id: str | int) -> dict | None:
        character = self.data.get(str(character_id))
        return dict(character) if character is not None else None

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
        return dict(self.data)

    def find_id_by_name(self, name: str) -> str | None:
        """Reverse of get_name() - the character id for a resolved display name."""
        if self._name_index is None:
            self._name_index = {}
            for character_id in self.data:
                resolved = self.get_name(character_id)
                if resolved:
                    self._name_index[resolved] = character_id

        return self._name_index.get(name)

    def __len__(self) -> int:
        return len(self.data)
