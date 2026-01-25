import logging
import time
from dataclasses import dataclass

import discord
from discord.ext import commands

from app.clients.warframe.worldstate.client import worldstate_client


class Alerts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="alerts", with_app_command=True, description="Data about current alerts."
    )
    async def alerts(self, ctx: commands.Context):
        """
        Usage: -alerts\n
        Data about current alerts
        """
        try:
            start = time.time()
            worldstate = await worldstate_client.get_worldstate()
            parsed_alerts = AlertsBuilder.parse_alerts(worldstate.alerts)

            message = AlertsBuilder.build_alerts_message(parsed_alerts)

            processing_time = round((time.time() - start) * 1000)
            message["embed"].set_footer(text=f"Processing time: {processing_time}ms")
            await ctx.send(**message)
        except Exception as e:
            self.logger.error(f"Error fetching alerts: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch alerts. Please try again later.",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Alerts(bot))


@dataclass(frozen=True)
class ParsedReward:
    name: str
    quantity: int


@dataclass(frozen=True)
class ParsedAlert:
    location: str
    mission_type: str
    faction: str
    min_level: int
    max_level: int
    expiry_ts: int
    max_waves: int | None
    rewards: list[ParsedReward]

    @property
    def display_key(self) -> str:
        return (
            f"{self.location} | {self.mission_type} | "
            f"{self.faction} | ({self.min_level}-{self.max_level})"
        )

    @property
    def expiry_text(self) -> str:
        return f"Ends: <t:{self.expiry_ts}:R>\n"

    @property
    def wave_text(self) -> str:
        return f"Waves: {self.max_waves}\n" if self.max_waves else ""


class AlertsBuilder:
    @staticmethod
    def parse_alerts(worldstate_alerts) -> list[ParsedAlert]:
        parsed_alerts: list[ParsedAlert] = []

        for alert in worldstate_alerts:
            info = alert.mission_info
            rewards = info.mission_reward

            parsed_rewards: list[ParsedReward] = []
            if rewards.credits:
                parsed_rewards.append(
                    ParsedReward(name="Credits", quantity=rewards.credits)
                )

            if rewards.items:
                for item in rewards.items:
                    parsed_rewards.append(ParsedReward(name=str(item), quantity=1))
            elif rewards.counted_items:
                for item in rewards.counted_items:
                    parsed_rewards.append(
                        ParsedReward(name=str(item.item), quantity=int(item.quantity))
                    )

            parsed_alerts.append(
                ParsedAlert(
                    location=info.location,
                    mission_type=info.mission_type,
                    faction=info.faction,
                    min_level=info.min_level,
                    max_level=info.max_level,
                    expiry_ts=int(alert.expiry.timestamp()),
                    max_waves=info.max_waves,
                    rewards=parsed_rewards,
                )
            )

        return parsed_alerts

    @staticmethod
    def build_alerts_message(parsed_alerts: list[ParsedAlert]) -> dict:
        embed = discord.Embed(color=discord.Colour.blue(), title="Alerts")

        if not parsed_alerts:
            embed.description = "There are no alerts currently running."
            embed.color = discord.Colour.red()
            return {"embed": embed}

        for alert in parsed_alerts:
            reward_text = "Rewards:\n"
            for reward in alert.rewards:
                reward_text += f"- **{reward.name}**: x{reward.quantity}\n"

            value = f"{alert.expiry_text}{alert.wave_text}{reward_text}"
            embed.add_field(name=alert.display_key, value=value, inline=False)

        return {"embed": embed}
