from datetime import datetime
from types import SimpleNamespace

from scripts.sheets.writer import SheetWriter


class FakeNanokaCharacters:
    def get_name(self, character_id):
        return {1: "Alice", 2: "Bob"}.get(character_id, str(character_id))


def _writer():
    writer = object.__new__(SheetWriter)
    writer.nanoka_characters = FakeNanokaCharacters()  # type: ignore
    return writer


def _char(char_id):
    return SimpleNamespace(id=char_id)


def _aa_record(with_boss_record=True):
    season = SimpleNamespace(
        end_time=SimpleNamespace(datetime=datetime(2026, 8, 25)),
        game_version="4.4",
    )
    mini_boss_records = [
        SimpleNamespace(id=801, characters=[_char(1), _char(2)], cycles_used=2),
        SimpleNamespace(id=802, characters=[_char(1), _char(2)], cycles_used=3),
    ]
    boss_record = SimpleNamespace(characters=[_char(1), _char(2)], cycles_used=5) if with_boss_record else None

    return SimpleNamespace(
        season=season, mini_boss_records=mini_boss_records, boss_record=boss_record,
    )


def test_build_aa_rows_numbers_knights_in_order():
    rows = _writer()._build_aa_rows(_aa_record())

    knight_1, knight_2 = rows[0], rows[1]
    assert knight_1[3] == "Knight 1"
    assert knight_2[3] == "Knight 2"


def test_build_aa_rows_leaves_notes_blank():
    rows = _writer()._build_aa_rows(_aa_record())

    assert all(row[4] == "" for row in rows)


def test_build_aa_rows_king_row_present():
    rows = _writer()._build_aa_rows(_aa_record())

    king = rows[-1]
    assert king[2] == "Anomaly Arbitration: King"
    assert king[4] == ""


def test_build_aa_rows_skips_king_row_when_no_boss_record():
    rows = _writer()._build_aa_rows(_aa_record(with_boss_record=False))

    assert all(row[2] != "Anomaly Arbitration: King" for row in rows)
