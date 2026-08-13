from datetime import datetime
from zoneinfo import ZoneInfo

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