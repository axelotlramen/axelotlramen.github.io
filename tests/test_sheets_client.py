from scripts.sheets.sheets_client import GoogleSheetsClient, _diff_rows, _preserve_manual_scores, _sort_key


class FakeWorksheet:
    """Minimal stand-in for gspread.Worksheet, backed by a plain list of rows."""

    def __init__(self, rows):
        self.rows = [list(r) for r in rows]

    def get_all_values(self):
        return [list(r) for r in self.rows]

    def insert_rows(self, rows, row):
        self.rows[row - 1:row - 1] = [list(r) for r in rows]

    def delete_rows(self, row_number):
        del self.rows[row_number - 1]


def _client(worksheet):
    client = object.__new__(GoogleSheetsClient)
    client._get_endgame_worksheet = lambda: worksheet
    return client


HEADER = ["Date", "Version", "Mode", "Side", "Notes", "M1", "M2", "M3", "M4", "Score"]


def test_preserve_manual_scores_fills_blank_moc_score():
    previous = [["01/01/2026", "4.4", "Memory of Chaos 4 Starward", "Node 1", "", "A", "B", "", "", "3000"]]
    new = [["01/02/2026", "4.4", "Memory of Chaos 4 Starward", "Node 1", "", "A", "B", "", "", ""]]

    result = _preserve_manual_scores(previous, new)

    assert result[0][-1] == "3000"


def test_preserve_manual_scores_does_not_overwrite_a_real_new_score():
    previous = [["01/01/2026", "4.4", "Apocalyptic Shadow 4 Starward", "Node 1", "", "A", "B", "", "", "3000"]]
    new = [["01/02/2026", "4.4", "Apocalyptic Shadow 4 Starward", "Node 1", "", "A", "B", "", "", "3600"]]

    result = _preserve_manual_scores(previous, new)

    assert result[0][-1] == "3600"


def test_diff_rows_flags_new_side_and_changed_score():
    previous = [["01/01/2026", "4.4", "Apocalyptic Shadow 4 Starward", "Node 1", "", "A", "B", "", "", "3000"]]
    new = [
        ["01/02/2026", "4.4", "Apocalyptic Shadow 4 Starward", "Node 1", "", "A", "B", "", "", "3600"],
        ["01/02/2026", "4.4", "Apocalyptic Shadow 4 Starward", "Node 2", "", "C", "D", "", "", "3000"],
    ]

    lines = _diff_rows(previous, new)

    assert any("3000 → 3600" in line for line in lines)
    assert any("🆕 Node 2" in line for line in lines)


def test_sort_key_orders_newest_version_first_then_mode_order():
    key_44_aa = _sort_key("4.4", "Anomaly Arbitration")
    key_44_apoc = _sort_key("4.4", "Apocalyptic Shadow 4 Starward")
    key_43_aa = _sort_key("4.3", "Anomaly Arbitration")

    assert key_44_aa < key_44_apoc  # AA sorts above Apoc within the same version
    assert key_44_aa < key_43_aa  # 4.4 sorts above 4.3


def test_upsert_rows_inserts_before_deleting_so_nothing_is_ever_lost():
    """Regression test for the delete-then-insert data-loss bug: old rows must still be
    present on the sheet at the moment the new rows are inserted."""
    old_block = ["01/01/2026", "4.4", "Apocalyptic Shadow 4 Starward", "Node 1", "", "A", "B", "", "", "3000"]
    worksheet = FakeWorksheet([HEADER, old_block])
    client = _client(worksheet)

    new_rows = [["01/02/2026", "4.4", "Apocalyptic Shadow 4 Starward", "Node 1", "", "A", "B", "", "", "3600"]]

    result = client.upsert_rows(new_rows)

    assert worksheet.rows == [HEADER, new_rows[0]]
    assert result.changed is True
    assert "3000 → 3600" in result.diff_lines[0]


def test_upsert_rows_no_rows_is_a_noop():
    worksheet = FakeWorksheet([HEADER])
    client = _client(worksheet)

    result = client.upsert_rows([])

    assert result.changed is False
    assert worksheet.rows == [HEADER]
