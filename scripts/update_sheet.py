import asyncio
import logging
import os

import genshin

from scripts.constants import MODE_LABELS, ModeReport
from scripts.logging_config import setup_logging
from scripts.notifier import EmbedBuilder, WebhookClient
from scripts.sheets.enums import ChallengeMode
from scripts.sheets.sheets_client import GoogleSheetsClient
from scripts.sheets.version import VersionResolver
from scripts.sheets.writer import SheetWriter

# Fetch/log order only - sheets_client.py keeps the sheet itself sorted.
DAILY_MODES = (ChallengeMode.APOC, ChallengeMode.PF, ChallengeMode.MOC, ChallengeMode.AA)

logger = logging.getLogger("hsr_sheet_automate")


async def run() -> None:
    notifier = WebhookClient(
        hoyolab_webhook=os.environ["HOYOLAB_WEBHOOK"],
        discord_id=os.environ["DISCORD_ID"],
    )
    reported = False

    try:
        logger.info("Starting daily HSR endgame sheet update")

        genshin_client = genshin.Client()
        genshin_client.set_cookies(os.environ["HOYOLAB_USER_COOKIES"])
        uid = int(os.environ["HOYOLAB_HSR_UID"])

        writer = await SheetWriter.create(
            genshin_client, uid, GoogleSheetsClient(), VersionResolver()
        )

        reports = []
        for mode in DAILY_MODES:
            label = MODE_LABELS.get(mode, mode.value)
            logger.info(f"Fetching {label}...")
            try:
                result = await writer.write_mode(mode)
                reports.append(
                    ModeReport(
                        mode=mode,
                        changed=result.changed,
                        diff_lines=result.diff_lines,
                        version=result.version,
                    )
                )
                logger.info(f"{label}: {'updated' if result.changed else 'no changes'}")
            except Exception as error:
                reports.append(ModeReport(mode=mode, error=str(error)))
                logger.error(f"{label}: failed - {error}")

        failed_modes = [report.mode.value for report in reports if report.error]

        notifier.send_hoyolab(elapsed=0.0, embeds=[EmbedBuilder.hsr_sheet_summary(reports)])
        logger.info("Sent daily sheet summary to Discord")

        if failed_modes:
            try:
                notifier.send_failure("HSR Sheet Update", f"Modes failed: {', '.join(failed_modes)}")
            except Exception:
                logger.exception("Failure alert also failed to send")
        reported = True

        if failed_modes:
            raise RuntimeError(f"Modes failed: {', '.join(failed_modes)}")

        logger.info("Daily HSR endgame sheet update finished successfully")

    except Exception as error:
        logger.error(f"Sheet update failed: {error}")
        if not reported:
            try:
                notifier.send_failure("HSR Sheet Update (setup)", str(error))
            except Exception:
                logger.exception("Failure notification also failed")
        raise

    finally:
        notifier.close()


if __name__ == "__main__":
    setup_logging(debug=True)
    asyncio.run(run())
