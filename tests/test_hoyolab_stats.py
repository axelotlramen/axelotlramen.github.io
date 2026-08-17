from types import SimpleNamespace

from scripts.hoyolab.stats import build_genshin_character, build_hsr_character


def _hsr_char(path=6, equip=None):
    return SimpleNamespace(icon="icon.png", rank=1, element="fire", path=path, level=80, equip=equip)


def test_build_hsr_character_known_path():
    char = build_hsr_character(_hsr_char(path=6))
    assert char["path"] == "PRESERVATION"


def test_build_hsr_character_unknown_path_falls_back():
    char = build_hsr_character(_hsr_char(path=999))
    assert char["path"] == "Unknown (999)"


def test_build_hsr_character_no_light_cone():
    char = build_hsr_character(_hsr_char(equip=None))
    assert char["lc"] is None


def _genshin_char(weapon_type=1, weapon=None):
    return SimpleNamespace(
        icon="icon.png", constellation=0, element="Pyro", weapon_type=weapon_type,
        level=90, friendship=10, weapon=weapon,
    )


def test_build_genshin_character_known_weapon_type():
    char = build_genshin_character(_genshin_char(weapon_type=11))
    assert char["weaponType"] == "CLAYMORE"


def test_build_genshin_character_unknown_weapon_type_falls_back():
    char = build_genshin_character(_genshin_char(weapon_type=999))
    assert char["weaponType"] == "Unknown (999)"
