import logging
import os
from pathlib import Path

import pandas as pd

from scripts.constants import UsageChange
from scripts.logging_config import setup_logging
from scripts.notifier import EmbedBuilder, WebhookClient
from scripts.sheets.sheets_client import GoogleSheetsClient

DATA_DIR = Path("data")
OVERALL_CSV = DATA_DIR / "usage_overall.csv"
BY_ENDGAME_CSV = DATA_DIR / "usage_by_endgame.csv"

# Add the new patch here when it drops; the newest entry is always "current".
PATCH_THRESHOLDS = (2.0, 3.0, 4.0)
CURRENT_THRESHOLD = PATCH_THRESHOLDS[-1]

MEMBER_COLUMNS = ["Member 1", "Member 2", "Member 3", "Member 4"]
TOP_UNITS_COUNT = 10

# Groups older/renamed "Endgame Type" sheet labels under one canonical name for counting.
ENDGAME_TYPE_ALIASES: dict[str, list[str]] = {
    "Apocalyptic Shadow": ["Apocalyptic Shadow 4", "Apocalyptic Shadow 4 Starward"],
    "Pure Fiction": ["Pure Fiction 4", "Pure Fiction 4 Starward"],
    "Memory of Chaos": ["Memory of Chaos 4", "Memory of Chaos 4 Starward"],
}
_ENDGAME_TYPE_LOOKUP = {
    raw: canonical for canonical, raws in ENDGAME_TYPE_ALIASES.items() for raw in raws
}


def _load_dataframe() -> pd.DataFrame:
    header, *rows = GoogleSheetsClient().get_all_rows()
    df = pd.DataFrame(rows, columns=header)
    df["Patch"] = pd.to_numeric(df["Patch"], errors="coerce")
    df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
    df["Endgame Type"] = df["Endgame Type"].replace(_ENDGAME_TYPE_LOOKUP)
    return df


def _melt_units(df: pd.DataFrame) -> pd.DataFrame:
    """One row per character appearance across the Member columns."""
    long_df = df.melt(
        id_vars=["Endgame Type", "Score"], value_vars=MEMBER_COLUMNS, value_name="Unit"
    )
    return long_df[long_df["Unit"] != ""]  # type: ignore


def _patch_buckets() -> list[tuple[float, float]]:
    """(lower, upper) patch bounds per major version; the newest bucket has no upper bound."""
    return [
        (threshold, PATCH_THRESHOLDS[i + 1] if i + 1 < len(PATCH_THRESHOLDS) else float("inf"))
        for i, threshold in enumerate(PATCH_THRESHOLDS)
    ]


def _in_patch_bucket(df: pd.DataFrame, lower: float, upper: float) -> pd.DataFrame:
    return df[(df["Patch"] >= lower) & (df["Patch"] < upper)]  # type: ignore


def build_overall_usage(df: pd.DataFrame) -> pd.DataFrame:
    """Unit, usage count per major version (2.x/3.x/4.x), plus a lifetime Total Usage."""
    columns = []
    for lower, upper in _patch_buckets():
        subset = _melt_units(_in_patch_bucket(df, lower, upper))
        columns.append(subset["Unit"].value_counts().rename(f"Uses in {lower}"))
    columns.append(_melt_units(df)["Unit"].value_counts().rename("Total Usage"))

    result = pd.concat(columns, axis=1).fillna(0).astype(int)
    result.index.name = "Unit"
    result = result.reset_index()
    return result.sort_values(f"Uses in {CURRENT_THRESHOLD}", ascending=False).reset_index(drop=True)


def build_per_endgame_usage(df: pd.DataFrame) -> pd.DataFrame:
    """Endgame Type + Unit, usage count/avg score per major version, plus lifetime totals."""
    per_bucket = []
    for lower, upper in _patch_buckets():
        subset = _melt_units(_in_patch_bucket(df, lower, upper))
        grouped = subset.groupby(["Endgame Type", "Unit"])
        counts = grouped.size().rename(f"Uses in {lower}")  # type: ignore
        avg_scores = grouped["Score"].mean().rename(f"Avg Score in {lower}")  # type: ignore
        per_bucket.append(pd.concat([counts, avg_scores], axis=1))

    all_grouped = _melt_units(df).groupby(["Endgame Type", "Unit"])
    per_bucket.append(pd.concat([
        all_grouped.size().rename("Total Usage"),  # type: ignore
        all_grouped["Score"].mean().rename("Avg Score Overall"),  # type: ignore
    ], axis=1))

    result = pd.concat(per_bucket, axis=1)
    for lower, _ in _patch_buckets():
        result[f"Uses in {lower}"] = result[f"Uses in {lower}"].fillna(0).astype(int)
        result[f"Avg Score in {lower}"] = result[f"Avg Score in {lower}"].round(2)
    result["Total Usage"] = result["Total Usage"].fillna(0).astype(int)
    result["Avg Score Overall"] = result["Avg Score Overall"].round(2)

    return result.reset_index().sort_values(["Endgame Type", "Unit"]).reset_index(drop=True)


def _current_patch_changes(
    key_cols: list[str], previous: pd.DataFrame | None, current: pd.DataFrame
) -> list[UsageChange]:
    """Only the usage/average-score changes for CURRENT_THRESHOLD (the most recent patch)."""
    uses_col = f"Uses in {CURRENT_THRESHOLD}"
    avg_col = f"Avg Score in {CURRENT_THRESHOLD}"
    has_avg_col = avg_col in current.columns

    previous_indexed = previous.set_index(key_cols) if previous is not None else None
    # Guards against the columns not existing yet in an older previous.csv (e.g. right after a rename).
    previous_has_uses = previous_indexed is not None and uses_col in previous_indexed.columns
    previous_has_avg = previous_indexed is not None and avg_col in previous_indexed.columns
    current_indexed = current.set_index(key_cols)

    changes = []
    for key, row in current_indexed.iterrows():
        label = key if isinstance(key, str) else " / ".join(str(part) for part in key)  # type: ignore
        new_uses = int(row[uses_col])  # type: ignore
        new_avg = _clean_avg(row[avg_col]) if has_avg_col else None  # type: ignore

        if previous_has_uses and key in previous_indexed.index:  # type: ignore
            old_row = previous_indexed.loc[key]  # type: ignore
            old_uses = int(old_row[uses_col])
            old_avg = _clean_avg(old_row[avg_col]) if previous_has_avg else None
        else:
            old_uses, old_avg = 0, None

        if old_uses != new_uses or old_avg != new_avg:
            changes.append(UsageChange(label, old_uses, new_uses, old_avg, new_avg))

    return changes


def _clean_avg(value: float) -> float | None:
    return None if pd.isna(value) else float(value)


def build_top_units(
    overall_df: pd.DataFrame, top_n: int = TOP_UNITS_COUNT
) -> list[tuple[str, int]]:
    """Top N units by usage in CURRENT_THRESHOLD, across all endgames combined."""
    uses_col = f"Uses in {CURRENT_THRESHOLD}"
    top = overall_df.nlargest(top_n, uses_col)
    return [(unit, int(uses)) for unit, uses in zip(top["Unit"], top[uses_col])]


def _read_previous(path: Path) -> pd.DataFrame | None:
    return pd.read_csv(path) if path.exists() else None


logger = logging.getLogger("hsr_weekly_usage")


def run() -> None:
    notifier = WebhookClient(
        hoyolab_webhook=os.environ["HOYOLAB_WEBHOOK"],
        discord_id=os.environ["DISCORD_ID"],
    )

    try:
        logger.info("Starting weekly HSR character usage update")

        df = _load_dataframe()
        logger.info(f"Loaded {len(df)} row(s) from the sheet")

        overall_previous = _read_previous(OVERALL_CSV)
        by_endgame_previous = _read_previous(BY_ENDGAME_CSV)

        overall_current = build_overall_usage(df)
        by_endgame_current = build_per_endgame_usage(df)

        overall_changes = _current_patch_changes(["Unit"], overall_previous, overall_current)
        by_endgame_changes = _current_patch_changes(
            ["Endgame Type", "Unit"], by_endgame_previous, by_endgame_current
        )
        top_units = build_top_units(overall_current)
        logger.info(
            f"Computed usage tables: {len(overall_changes)} overall change(s), "
            f"{len(by_endgame_changes)} per-endgame change(s) for patch {CURRENT_THRESHOLD}"
        )

        DATA_DIR.mkdir(exist_ok=True)
        overall_current.to_csv(OVERALL_CSV, index=False)
        by_endgame_current.to_csv(BY_ENDGAME_CSV, index=False)
        logger.info(f"Wrote {OVERALL_CSV} and {BY_ENDGAME_CSV}")

        notifier.send_hoyolab(
            elapsed=0.0,
            embeds=EmbedBuilder.hsr_usage_summary(
                overall_changes, by_endgame_changes, top_units, CURRENT_THRESHOLD
            ),
        )
        logger.info("Sent weekly usage update to Discord")
        logger.info("Weekly HSR character usage update finished successfully")

    except Exception as error:
        logger.error(f"Weekly character usage update failed: {error}")
        try:
            notifier.send_failure("Weekly Character Usage Update", str(error))
        except Exception:
            logger.exception("Failure notification also failed")
        raise

    finally:
        notifier.close()


if __name__ == "__main__":
    setup_logging(debug=True)
    run()
