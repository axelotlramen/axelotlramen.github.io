from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo

from scripts.sheets.enums import ChallengeMode

TZ = ZoneInfo("America/New_York")

def now():
    """Return current time in the project timezone."""
    return datetime.now(TZ)

HSR_PATH_NUM_TO_NAME = {
    1: "DESTRUCTION",
    2: "THE HUNT",
    3: "ERUDITION",
    4: "HARMONY",
    5: "NIHILITY",
    6: "PRESERVATION",
    7: "ABUNDANCE",
    8: "REMEMBRANCE",
    9: "ELATION"
}

GENSHIN_WEAPON_NUM_TO_NAME = {
    1: "SWORD",
    10: "CATALYST",
    11: "CLAYMORE",
    12: "BOW",
    13: "POLEARM"
}

# Nanoka's string path codes - a different keyspace from HSR_PATH_NUM_TO_NAME above.
HSR_PATHS = {
    "Knight": "Preservation",
    "Rogue": "The Hunt",
    "Warrior": "Destruction",
    "Mage": "Erudition",
    "Shaman": "Harmony",
    "Warlock": "Nihility",
    "Priest": "Abundance",
    "Memory": "Remembrance",
    "Elation": "Elation",
}

HSR_SHORT_NAMES = {
    "Remembrance Trailblazer": "RMC",
    "Dan Heng • Permansor Terrae": "DHPT",
    "Mortenax Blade": "MBlade",
}

MODE_LABELS = {
    ChallengeMode.APOC: "Apocalyptic Shadow",
    ChallengeMode.PF: "Pure Fiction",
    ChallengeMode.AA: "Anomaly Arbitration",
    ChallengeMode.MOC: "Memory of Chaos",
}


@dataclass
class ModeReport:
    mode: ChallengeMode
    changed: bool = False
    diff_lines: list[str] = field(default_factory=list)
    error: str | None = None
    version: str | None = None


@dataclass
class UsageChange:
    """A unit's usage count/average score change, for the weekly usage report."""

    label: str
    old_uses: int
    new_uses: int
    old_avg_score: float | None = None
    new_avg_score: float | None = None