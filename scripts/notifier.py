import calendar
from datetime import timedelta
from typing import Any, Dict

import httpx

from scripts.constants import MODE_LABELS, now

GREEN_EMBED = 5763719
RED_EMBED = 15548997

class WebhookClient:
    def __init__(self, hoyolab_webhook: str, endfield_webhook: str | None = None, discord_id: str | None = None, timeout: int = 10):
        self.hoyolab_webhook = hoyolab_webhook
        self.endfield_webhook = endfield_webhook
        self.discord_id = discord_id
        self._http = httpx.Client(timeout=timeout)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "WebhookClient":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()

    def send_hoyolab(self, elapsed: float, embeds):
        payload = {
            "username": "Hoyolab Stats Bot",
            "content": f"✅ Task completed in `{elapsed:.2f}s`",
            "embeds": embeds
        }

        response = self._http.post(self.hoyolab_webhook, json=payload)
        response.raise_for_status()

    def send_endfield(self, elapsed: float, embeds):
        if not self.endfield_webhook:
            raise RuntimeError("WebhookClient was constructed without endfield_webhook")

        payload = {
            "username": "Chen Qianyu - Dijiang Control Nexus Assistant",
            "content": f"✅ Task completed in `{elapsed:.2f}s`",
            "embeds": embeds
        }

        response = self._http.post(self.endfield_webhook, json=payload)
        response.raise_for_status()

    def send_failure(self, task_name: str, error_message: str):
        now_est = now()

        embed = {
            "title": "Task Failure",
            "description": f"❌ **{task_name} Failed**\n\n```{error_message}```",
            "color": RED_EMBED,
            "footer": {
                "text": f"Time: {now_est.strftime('%m/%d/%Y, %I:%M:%S %p')} (ET)"
            }
        }

        payload = {
            "content": f"<@{self.discord_id}> Stats update failed!\n{error_message or ''}",
            "embeds": [embed]
        }

        response = self._http.post(self.hoyolab_webhook, json=payload)
        response.raise_for_status()


class EmbedBuilder:
    """Builds Discord embed payloads from stats snapshots. Pure/stateless — all methods are static."""

    @staticmethod
    def hoyolab_stats(old_data: dict | None, genshin_data: dict, hsr_data: dict):
        embed_color = GREEN_EMBED

        if old_data:
            old_genshin = old_data.get("genshin_data", {})
            old_hsr = old_data.get("hsr_data", {})
        else:
            old_genshin = {}
            old_hsr = {}

        fields = [
            {
                "name": "Genshin Impact",
                "value": (
                    f"**AR:** {genshin_data.get('level', 'N/A')}\n"
                    f"**Achievements:** {EmbedBuilder._delta(old_genshin.get('achievements', '0'), genshin_data.get('achievements', '0'))}\n"
                    f"**Active Days:** {EmbedBuilder._delta(old_genshin.get('active_days', '0'), genshin_data.get('active_days', '0'))}\n"
                    f"**Character Count:** {EmbedBuilder._delta(old_genshin.get('avatar_count', '0'), genshin_data.get('avatar_count', '0'))}\n"
                    f"**Oculus:** {EmbedBuilder._delta(old_genshin.get('oculus', '0'), genshin_data.get('oculus', '0'))}\n"
                    f"**Chest Count:** {EmbedBuilder._delta(old_genshin.get('chest_count', '0'), genshin_data.get('chest_count', '0'))}\n"
                    f"**Resin:** {EmbedBuilder._delta(old_genshin.get('resin', '0'), genshin_data.get('resin', '0'))}\n"
                    f"**Daily Tasks:** {EmbedBuilder._delta(old_genshin.get('daily_task', '0'), genshin_data.get('daily_task', '0'))}\n"
                ),
                "inline": True
            },
            {
                "name": "Honkai: Star Rail",
                "value": (
                    f"**Trailblaze Level:** {hsr_data.get('level', 'N/A')}\n"
                    f"**Achievements:** {EmbedBuilder._delta(old_hsr.get('achievements', '0'), hsr_data.get('achievements', '0'))}\n"
                    f"**Active Days:** {EmbedBuilder._delta(old_hsr.get('active_days', '0'), hsr_data.get('active_days', '0'))}\n"
                    f"**Character Count:** {EmbedBuilder._delta(old_hsr.get('avatar_count', '0'), hsr_data.get('avatar_count', '0'))}\n"
                    f"**Chest Count:** {EmbedBuilder._delta(old_hsr.get('chest_count', '0'), hsr_data.get('chest_count', '0'))}\n"
                    f"**Trailblaze Power:** {EmbedBuilder._delta(old_hsr.get('stamina', '0'), hsr_data.get('stamina', '0'))}\n"
                    f"**Daily Training:** {EmbedBuilder._delta(old_hsr.get('current_train_score', '0'), hsr_data.get('current_train_score', '0'))}\n"
                ),
                "inline": True
            }
        ]

        now_est = now()

        return {
            "title": "Hoyolab Stats Updated",
            "description": "✅ **Site updated successfully!**",
            "color": embed_color,
            "fields": fields,
            "footer": {
                "text": f"Time: {now_est.strftime('%m/%d/%Y, %I:%M:%S %p')} (ET)",
                "icon_url": "https://www.hoyolab.com/favicon.ico"
            }
        }

    @staticmethod
    def hoyolab_diary(hsr_diary: dict | None, genshin_diary: dict | None):
        embed_color = GREEN_EMBED

        now_est = now()

        fields = []

        if genshin_diary:
            fields.append({
                "name": "Genshin Impact",
                "value": (
                    f"**Net Currency Gain:** {genshin_diary.get('Net Currency Gain', '0')}\n"
                    f"**Pulls Net Gain:** {genshin_diary.get('Pulls Net Gain', '0')}\n"
                ),
                "inline": True
            })

        if hsr_diary:
            fields.append({
                "name": "Honkai: Star Rail",
                "value": (
                    f"**Net Currency Gain:** {hsr_diary.get('Net Currency Gain', '0')}\n"
                    f"**Pulls Net Gain:** {hsr_diary.get('Pulls Net Gain', '0')}\n"
                ),
                "inline": True
            })

        return {
            "title": "Daily Pull Progress Update",
            "description": "📈 **Diary Updated Successfully**",
            "color": embed_color,
            "fields": fields,
            "footer": {
                "text": f"Time: {now_est.strftime('%m/%d/%Y, %I:%M:%S %p')} (ET)",
                "icon_url": "https://www.hoyolab.com/favicon.ico"
            }
        }

    @staticmethod
    def endfield_attendance(results: Dict[str, Any]):
        embed_color = GREEN_EMBED

        now_est = now()

        rewards_text = ", ".join(f"{r['name']} x{r['count']}" for r in results.get("rewards", []))
        rewards_icon_url = results.get("rewards", [])[0].get("icon", "") if results.get("rewards", []) else ""

        currentSignIns = int(results.get("attendance", {}).get("totalSignIns", 0))

        tomorrow = now() + timedelta(days=1)
        total_days = calendar.monthrange(tomorrow.year, tomorrow.month)[1]

        # Current reward embed
        current_embed = {
            "title": ":date: Daily Sign-In",
            "color": embed_color,
            "fields": [
                {
                    "name": "Status",
                    "value": results.get("status") or "-"
                },
                {
                    "name": "Claimed Rewards" if results.get("status") == "Already Claimed" else "Rewards",
                    "value": rewards_text
                },
                {
                    "name": "Progress",
                    "value": f"{currentSignIns}/{total_days}"
                }
            ],
            "footer": {
                "text": f"Time: {now_est.strftime('%m/%d/%Y, %I:%M:%S %p')} (ET)",
                "icon_url": "https://assets.skport.com/assets/favicon.ico"
            }
        }

        if rewards_icon_url:
            current_embed["thumbnail"] = {"url": rewards_icon_url}

        embeds = [current_embed]

        # Next reward embed (only if nextAward exists)
        next_award = results.get("nextAward")
        if next_award and next_award.get("name"):
            next_rewards_text = f"{next_award.get('name')} x{next_award.get('count')}"
            next_icon_url = next_award.get("icon", "")

            next_embed = {
                "title": ":track_next: Next Reward",
                "color": embed_color,
                "fields": [
                    {
                        "name": "Next Reward",
                        "value": next_rewards_text
                    }
                ]
            }

            if next_icon_url:
                next_embed["thumbnail"] = {"url": next_icon_url}

            embeds.append(next_embed)

        return embeds

    @staticmethod
    def endfield_stats(old_data: dict | None, endfield_data: dict):
        embed_color = GREEN_EMBED

        if old_data:
            old_endfield = old_data.get("endfield_data", {})
        else:
            old_endfield = {}

        fields = [
            {
                "name": "Arknights: Endfield",
                "value": (
                    f"**Level:** {endfield_data.get('level', 'N/A')}\n"
                    f"**Achievements:** {EmbedBuilder._delta(old_endfield.get('achievements', 0), endfield_data.get('achievements', '0'))}\n"
                    f"**Active Days:** {EmbedBuilder._delta(old_endfield.get('active_days', '0'), endfield_data.get('active_days', '0'))}\n"
                    f"**Character Count:** {EmbedBuilder._delta(old_endfield.get('avatar_count', '0'), endfield_data.get('avatar_count', '0'))}\n"
                    f"**Aurylenes:** {EmbedBuilder._delta(old_endfield.get('aurylenes', '0'), endfield_data.get('aurylenes', '0'))}\n"
                    f"**Chest Count:** {EmbedBuilder._delta(old_endfield.get('chest_count', '0'), endfield_data.get('chest_count', '0'))}\n"
                    f"**Stamina:** {EmbedBuilder._delta(old_endfield.get('stamina', '0'), endfield_data.get('stamina', '0'))}\n"
                    f"**Daily Mission:** {EmbedBuilder._delta(old_endfield.get('daily_mission', '0'), endfield_data.get('daily_mission', '0'))}\n"
                )
            }
        ]

        now_est = now()

        return {
            "title": "Arknights: Endfield Stats Updated",
            "description": "✅ **Site updated successfully!**",
            "color": embed_color,
            "fields": fields,
            "footer": {
                "text": f"Time: {now_est.strftime('%m/%d/%Y, %I:%M:%S %p')} (ET)",
                "icon_url": "https://assets.skport.com/assets/favicon.ico"
            }
        }

    @staticmethod
    def hsr_sheet_summary(reports):
        """One embed summarizing every HSR endgame mode's sheet-write result."""
        has_errors = any(report.error for report in reports)
        has_changes = any(report.changed for report in reports)

        if has_errors:
            description = "⚠️ **Daily HSR sheet update finished with errors.**"
        elif has_changes:
            description = "📊 **Daily HSR sheet update — new results today.**"
        else:
            description = "✅ **Daily HSR sheet update — no changes.**"

        now_est = now()

        return {
            "title": "Daily HSR Endgame Sheet Update",
            "description": description,
            "color": RED_EMBED if has_errors else GREEN_EMBED,
            "fields": [EmbedBuilder._sheet_report_field(report) for report in reports],
            "footer": {
                "text": f"Time: {now_est.strftime('%m/%d/%Y, %I:%M:%S %p')} (ET)"
            }
        }

    @staticmethod
    def _sheet_report_field(report):
        label = MODE_LABELS.get(report.mode, report.mode.value)
        if report.version:
            label = f"{label} (v{report.version})"

        if report.error:
            value = f"❌ ```{report.error}```"
        elif report.diff_lines:
            value = "\n".join(report.diff_lines)
        else:
            value = "No changes"

        return {"name": label, "value": value, "inline": False}

    @staticmethod
    def hsr_usage_summary(overall_changes, by_endgame_changes, top_units, current_patch):
        """Two embeds: the weekly usage-change summary, and a top-10 leaderboard."""
        has_changes = bool(overall_changes or by_endgame_changes)

        description = (
            f"📈 **Weekly character usage update — changes in patch {current_patch}.**"
            if has_changes
            else f"✅ **Weekly character usage update — no changes in patch {current_patch}.**"
        )

        change_fields = []
        if overall_changes:
            table = EmbedBuilder._render_table(
                ["Unit", f"Uses in {current_patch}"],
                [
                    [change.label, f"{change.old_uses} → {change.new_uses}"]
                    for change in overall_changes
                ],
            )
            change_fields.append({"name": "All Endgames", "value": table})

        if by_endgame_changes:
            table = EmbedBuilder._render_table(
                ["Endgame / Unit", "Uses", "Avg Score"],
                [
                    [
                        change.label,
                        f"{change.old_uses} → {change.new_uses}",
                        EmbedBuilder._format_avg_change(change.old_avg_score, change.new_avg_score),
                    ]
                    for change in by_endgame_changes
                ],
            )
            change_fields.append({"name": "Per Endgame", "value": table})

        if not change_fields:
            change_fields.append({
                "name": "Status",
                "value": f"No usage changes in patch {current_patch}."
            })

        now_est = now()

        embeds = [{
            "title": f"Weekly Usage Changes (Patch {current_patch})",
            "description": description,
            "color": GREEN_EMBED,
            "fields": change_fields,
            "footer": {
                "text": f"Time: {now_est.strftime('%m/%d/%Y, %I:%M:%S %p')} (ET)"
            }
        }]

        if top_units:
            leaderboard = EmbedBuilder._render_table(
                ["#", "Unit", f"Uses in {current_patch}"],
                [
                    [str(rank), unit, str(uses)]
                    for rank, (unit, uses) in enumerate(top_units, start=1)
                ],
            )
            embeds.append({
                "title": f"Top {len(top_units)} Units in Patch {current_patch}",
                "color": GREEN_EMBED,
                "description": leaderboard,
            })

        return embeds

    @staticmethod
    def _render_table(headers, rows, limit: int = 1000):
        """Render a monospace table (in a code block) for Discord, truncated to fit one field."""
        widths = [len(header) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(cell))

        def format_row(cells):
            return "  ".join(cell.ljust(width) for cell, width in zip(cells, widths))

        lines = [format_row(headers), format_row(["-" * width for width in widths])]
        lines.extend(format_row(row) for row in rows)

        body = "\n".join(lines)
        if len(body) > limit:
            truncated = body[:limit].rsplit("\n", 1)[0]
            body = f"{truncated}\n… ({len(rows)} rows total)"

        return f"```\n{body}\n```"

    @staticmethod
    def _format_avg_score(value):
        return "-" if value is None else f"{value:.2f}"

    @staticmethod
    def _format_avg_change(old_value, new_value):
        return f"{EmbedBuilder._format_avg_score(old_value)} → {EmbedBuilder._format_avg_score(new_value)}"

    @staticmethod
    def _delta(old_value, new_value):
        try:
            old_value = int(old_value)
            new_value = int(new_value)
            diff = new_value - old_value

            if diff > 0:
                return f"{new_value} (+{diff})"
            elif diff < 0:
                return f"{new_value} ({diff})"
            else:
                return f"{new_value}"
        except Exception:
            return str(new_value)
