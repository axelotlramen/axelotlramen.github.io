import enum
from typing import Any

SheetRow = list[Any]


class ChallengeMode(str, enum.Enum):
    """Internal identifier for which HSR endgame mode to fetch and write."""

    APOC = "apoc"
    PF = "pf"
    AA = "aa"
    MOC = "moc"


class HSRMode(str, enum.Enum):
    """Exact literal strings written to the sheet's Mode column."""

    APOC = "Apocalyptic Shadow 4 Starward"
    PF = "Pure Fiction 4 Starward"
    MOC = "Memory of Chaos 4 Starward"
    AA = "Anomaly Arbitration"
    AA_KING = "Anomaly Arbitration: King"
