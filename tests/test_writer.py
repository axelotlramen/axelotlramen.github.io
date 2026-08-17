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
    mini_bosses = [
        SimpleNamespace(id=801, name="Argenti Knight (I)"),
        SimpleNamespace(id=802, name="Svarog Knight (II)"),
    ]
    boss_record = SimpleNamespace(characters=[_char(1), _char(2)], cycles_used=5) if with_boss_record else None
    boss = SimpleNamespace(name="Murata Graphia, Founding Artist")

    return SimpleNamespace(
        season=season, mini_boss_records=mini_boss_records, mini_bosses=mini_bosses,
        boss_record=boss_record, boss=boss,
    )


def test_build_aa_rows_fills_in_mini_boss_names_by_id():
    rows = _writer()._build_aa_rows(_aa_record())

    knight_1, knight_2 = rows[0], rows[1]
    assert knight_1[3] == "Knight 1"
    assert knight_1[4] == "Argenti Knight (I)"
    assert knight_2[4] == "Svarog Knight (II)"


def test_build_aa_rows_fills_in_boss_name_for_king_row():
    rows = _writer()._build_aa_rows(_aa_record())

    king = rows[-1]
    assert king[2] == "Anomaly Arbitration: King"
    assert king[4] == "Murata Graphia, Founding Artist"


def test_build_aa_rows_skips_king_row_when_no_boss_record():
    rows = _writer()._build_aa_rows(_aa_record(with_boss_record=False))

    assert all(row[2] != "Anomaly Arbitration: King" for row in rows)


def test_build_aa_rows_unknown_mini_boss_id_falls_back_to_blank_note():
    record = _aa_record()
    record.mini_bosses = [SimpleNamespace(id=999, name="Someone Else")]  # no id 801/802 defined

    rows = _writer()._build_aa_rows(record)

    assert rows[0][4] == ""  # no matching definition for id 801 - blank, not a crash
