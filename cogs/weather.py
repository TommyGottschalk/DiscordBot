"""Cog — Weather.

Fetches current conditions and a 3-day forecast from Open-Meteo
(open-meteo.com — free, no API key required).

Commands
--------
$weather <city>  —  current conditions + 3-day forecast in °F
"""

from datetime import datetime

import aiohttp
import discord
from discord.ext import commands

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Short day-of-week labels indexed by Python's weekday() (0 = Monday).
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# WMO weather interpretation codes mapped to (description, emoji).
# Full spec: https://open-meteo.com/en/docs#weathervariables
WMO_CODES: dict[int, tuple[str, str]] = {
    0:  ("Clear Sky",               "☀️"),
    1:  ("Mainly Clear",            "🌤️"),
    2:  ("Partly Cloudy",           "⛅"),
    3:  ("Overcast",                "☁️"),
    45: ("Fog",                     "🌫️"),
    48: ("Icy Fog",                 "🌫️"),
    51: ("Light Drizzle",           "🌦️"),
    53: ("Moderate Drizzle",        "🌦️"),
    55: ("Heavy Drizzle",           "🌧️"),
    61: ("Light Rain",              "🌧️"),
    63: ("Moderate Rain",           "🌧️"),
    65: ("Heavy Rain",              "🌧️"),
    71: ("Light Snow",              "🌨️"),
    73: ("Moderate Snow",           "❄️"),
    75: ("Heavy Snow",              "❄️"),
    77: ("Snow Grains",             "🌨️"),
    80: ("Light Showers",           "🌦️"),
    81: ("Moderate Showers",        "🌧️"),
    82: ("Heavy Showers",           "⛈️"),
    85: ("Snow Showers",            "🌨️"),
    86: ("Heavy Snow Showers",      "❄️"),
    95: ("Thunderstorm",            "⛈️"),
    96: ("Thunderstorm w/ Hail",    "⛈️"),
    99: ("Thunderstorm w/ Hail",    "⛈️"),
}


def wmo(code: int) -> tuple[str, str]:
    """Return (description, emoji) for a WMO weather code, with a safe fallback."""
    return WMO_CODES.get(code, ("Unknown", "🌡️"))


class Weather(commands.Cog):
    """Current conditions and 3-day forecast via Open-Meteo."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name='weather')
    async def weather(self, ctx: commands.Context, *, city: str) -> None:
        """Show current weather and a 3-day forecast for any city.

        Temperatures in °F. Powered by Open-Meteo (no API key required).

        Usage: $weather <city>
        Examples:
            $weather London
            $weather New York
            $weather São Paulo
        """
        async with aiohttp.ClientSession() as session:

            # ── Step 1: resolve city name → lat/lon via Open-Meteo geocoding ──
            async with session.get(
                GEOCODE_URL,
                params={"name": city, "count": 1, "language": "en", "format": "json"},
            ) as geo_resp:
                if geo_resp.status != 200:
                    await ctx.send("Geocoding service is unavailable. Try again later.")
                    return
                geo_data = await geo_resp.json()

            if not geo_data.get("results"):
                await ctx.send(f"Couldn't find a location called **{city}**. Check your spelling.")
                return

            loc = geo_data["results"][0]
            lat, lon = loc["latitude"], loc["longitude"]
            location_name = f"{loc['name']}, {loc.get('country_code', '').upper()}"

            # ── Step 2: fetch current conditions + 4 days of daily data ───────
            # We request 4 days so index 0 = today (for current label) and
            # indices 1–3 give us tomorrow + 2 more for the 3-day forecast.
            async with session.get(
                FORECAST_URL,
                params={
                    "latitude":         lat,
                    "longitude":        lon,
                    "current":          "temperature_2m,weathercode,windspeed_10m,relativehumidity_2m",
                    "daily":            "weathercode,temperature_2m_max,temperature_2m_min",
                    "temperature_unit": "fahrenheit",
                    "windspeed_unit":   "mph",
                    "timezone":         "auto",
                    "forecast_days":    4,
                },
            ) as wx_resp:
                if wx_resp.status != 200:
                    await ctx.send("Weather service is unavailable. Try again later.")
                    return
                wx = await wx_resp.json()

        current = wx["current"]
        daily   = wx["daily"]

        temp     = round(current["temperature_2m"])
        humidity = current["relativehumidity_2m"]
        wind     = round(current["windspeed_10m"])
        cond_desc, cond_emoji = wmo(current["weathercode"])

        # ── Build embed ────────────────────────────────────────────────────
        embed = discord.Embed(
            title=f"{cond_emoji}  Weather for {location_name}",
            color=discord.Color.blue(),
        )
        embed.add_field(
            name="Now",
            value=f"**{temp}°F** — {cond_desc}\n💨 {wind} mph  |  💧 {humidity}%",
            inline=False,
        )

        # Build the 3-day forecast, skipping index 0 (today).
        forecast_lines = []
        for i in range(1, 4):
            date_str = daily["time"][i]          # "YYYY-MM-DD"
            day_name = DAYS[datetime.strptime(date_str, "%Y-%m-%d").weekday()]
            hi = round(daily["temperature_2m_max"][i])
            lo = round(daily["temperature_2m_min"][i])
            d_desc, d_emoji = wmo(daily["weathercode"][i])
            forecast_lines.append(f"{day_name}  {d_emoji}  {lo}°–{hi}°F  —  {d_desc}")

        embed.add_field(
            name="3-Day Forecast",
            value="\n".join(forecast_lines),
            inline=False,
        )
        embed.set_footer(text="Powered by Open-Meteo · open-meteo.com")

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Weather(bot))
