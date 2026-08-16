import bisect
import datetime
import json
from pathlib import Path

DEFAULT_VERSION_FILE = Path("data/version.json")


class VersionResolver:
    """Resolves a date to the HSR version whose range it falls into, per data/version.json."""

    def __init__(self, path: Path = DEFAULT_VERSION_FILE) -> None:
        versions: dict[str, str] = json.loads(path.read_text())
        self._entries = sorted(
            (datetime.date.fromisoformat(start), version)
            for version, start in versions.items()
        )

    def resolve(self, date: datetime.date) -> str:
        starts = [start for start, _ in self._entries]
        index = bisect.bisect_right(starts, date) - 1
        if index < 0:
            earliest = self._entries[0][0]
            raise ValueError(f"{date} is before the earliest known version ({earliest})")

        return self._entries[index][1]
