import asyncio
import json
import logging
import os
import time
from pathlib import Path

import genshin
import pandas as pd

from scripts.constants import HSR_SHORT_NAMES, now
from scripts.endfield.client import EndfieldClient
from scripts.hoyolab.diary import GENSHIN_CONFIG, HSR_CONFIG, DiaryWorkbook
from scripts.hoyolab.stats import HoyolabStatsFetcher
from scripts.logging_config import setup_logging
from scripts.notifier import EmbedBuilder, WebhookClient
from scripts.update_usage import CURRENT_THRESHOLD

USAGE_CSV = Path("data/usage_overall.csv")


def _order_hsr_by_usage(five_star_characters: dict) -> dict:
    """Order HSR characters by current-patch endgame usage; falls back to level, then to
    whatever order five_star_characters is already in if the usage CSV isn't there yet."""
    if not USAGE_CSV.exists():
        return five_star_characters

    usage_df = pd.read_csv(USAGE_CSV)
    uses_col = f"Uses in {CURRENT_THRESHOLD}"
    if uses_col not in usage_df.columns:
        return five_star_characters

    usage_by_name = dict(zip(usage_df["Unit"], usage_df[uses_col]))

    def usage_for(name: str) -> int:
        short_name = HSR_SHORT_NAMES.get(name, name)
        return usage_by_name.get(short_name, usage_by_name.get(name, 0))

    ordered = sorted(
        five_star_characters.items(),
        key=lambda item: (usage_for(item[0]), item[1]["level"]),
        reverse=True,
    )
    return dict(ordered)


class StatsUpdatePipeline:
    def __init__(self):
        self.notifier = WebhookClient(
            hoyolab_webhook=os.environ["HOYOLAB_WEBHOOK"],
            endfield_webhook=os.environ["ENDFIELD_WEBHOOK"],
            discord_id=os.environ["DISCORD_ID"]
        )

        hoyolab_client = genshin.Client()
        hoyolab_client.set_cookies(os.environ["HOYOLAB_USER_COOKIES"])
        self.hoyolab_client = hoyolab_client
        self.stats_fetcher = HoyolabStatsFetcher(hoyolab_client)

        self.hsr_uid = int(os.environ["HOYOLAB_HSR_UID"])
        self.genshin_uid = int(os.environ["HOYOLAB_GENSHIN_UID"])

        self.hsr_diary = DiaryWorkbook(HSR_CONFIG)
        self.genshin_diary = DiaryWorkbook(GENSHIN_CONFIG)

        self.endfield_client = EndfieldClient(
            cred=os.environ["ENDFIELD_CRED"],
            sk_game_role=os.environ["ENDFIELD_GAME_ROLE"]
        )

    async def run(self):
        start_time = time.perf_counter()
        logger = logging.getLogger("main")

        try:
            # ---------------------------
            # Load previous JSON
            # ---------------------------
            old_data = None

            if os.path.exists("data/stats.json"):
                try:
                    with open("data/stats.json", "r") as f:
                        old_data = json.load(f)
                except Exception:
                    old_data = {}

            # ---------------------------
            # Fetch Data
            # ---------------------------
            hsr_data = await self.stats_fetcher.fetch_hsr(self.hsr_uid)
            if hsr_data.get("five_star_characters"):
                hsr_data["five_star_characters"] = _order_hsr_by_usage(hsr_data["five_star_characters"])
            genshin_data = await self.stats_fetcher.fetch_genshin(self.genshin_uid)
            hsr_diary = await self.hsr_diary.update(self.hoyolab_client, self.hsr_uid)
            genshin_diary = await self.genshin_diary.update(self.hoyolab_client, self.genshin_uid)

            endfield_attendance = self.endfield_client.claim_attendance()
            endfield_data = self.endfield_client.fetch_endfield_data(old_data.get("endfield_data", {}) if old_data else {})

            data = {
                "last_updated": now().isoformat(),
                "hsr_data": hsr_data,
                "genshin_data": genshin_data,
                "hsr_diary": hsr_diary,
                "genshin_diary": genshin_diary,
                "endfield_attendance": endfield_attendance,
                "endfield_data": endfield_data
            }

            os.makedirs("data", exist_ok=True)

            with open("data/stats.json", "w") as f:
                json.dump(data, f, indent=2)

            # ---------------------------
            # SUCCESS NOTIFICATION
            # ---------------------------
            elapsed = time.perf_counter() - start_time
            logger.info(f"Stats update completed in {elapsed:.2f}s")

            self.notifier.send_hoyolab(
                elapsed=elapsed,
                embeds=[
                    EmbedBuilder.hoyolab_stats(
                        old_data=old_data,
                        genshin_data=genshin_data,
                        hsr_data=hsr_data
                    ),
                    EmbedBuilder.hoyolab_diary(
                        hsr_diary=hsr_diary,
                        genshin_diary=genshin_diary
                    )
                ]
            )

            self.notifier.send_endfield(
                elapsed=elapsed,
                embeds=[
                    *EmbedBuilder.endfield_attendance(endfield_attendance), # spread the list
                    EmbedBuilder.endfield_stats(
                        old_data=old_data,
                        endfield_data=endfield_data
                    ),
                ]
            )

        except Exception as e:
            # ---------------------------
            # FAILURE NOTIFICATION
            # ---------------------------

            self.notifier.send_failure(
                task_name="main",
                error_message=str(e)
            )
            raise


if __name__ == "__main__":
    setup_logging(debug=True)
    logging.info("Starting Stats Update Script")

    try:
        asyncio.run(StatsUpdatePipeline().run())
        logging.info("Script finished successfully.")
    except Exception:
        logging.exception("Script crashed.")
        raise
