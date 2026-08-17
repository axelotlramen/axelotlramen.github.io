from pydantic import BaseModel, ConfigDict, ValidationError


class LenientModel(BaseModel):
    """Base for stats.json section models: validates the fields we rely on, allows anything else."""

    model_config = ConfigDict(extra="allow")


class HSRData(LenientModel):
    nickname: str
    level: int
    avatar_url: str
    achievements: int
    active_days: int
    avatar_count: int
    chest_count: int
    five_star_characters: dict


class GenshinData(LenientModel):
    nickname: str
    level: int
    avatar_url: str
    achievements: int
    active_days: int
    avatar_count: int
    oculus: int
    chest_count: int
    five_star_characters: dict


class EndfieldData(LenientModel):
    nickname: str
    level: int
    avatar_url: str
    achievements: int
    active_days: int
    avatar_count: int
    aurylenes: int
    chest_count: int
    six_star_characters: dict


def is_valid_section(data: dict, model: type[LenientModel]) -> bool:
    """False for the {} failure sentinel, or anything missing the fields we depend on."""
    if not data:
        return False
    try:
        model.model_validate(data)
        return True
    except ValidationError:
        return False
