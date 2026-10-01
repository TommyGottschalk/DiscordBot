"""Cog — Help.

A custom, end-user-friendly replacement for discord.py's default help
command. Groups every other cog's commands into one easy-to-scan embed,
and can drill into a single command for full usage details.

Commands
--------
$help            —  list every command, grouped by category
$help <command>  —  show full usage details for one command
"""

from discord.ext import commands
import discord

NO_DESCRIPTION = "No description available."


def usage_string(prefix: str, command: commands.Command) -> str:
    """Build a "$name <args>" usage string, with no trailing space for argument-less commands."""
    if command.signature:
        return f"{prefix}{command.name} {command.signature}"
    return f"{prefix}{command.name}"


class Help(commands.Cog):
    """Lists every command and what it does, for end users."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="help", hidden=True)
    async def help_command(self, ctx: commands.Context, *, command_name: str | None = None) -> None:
        """Show every available command, or full details for one command.

        Usage: $help [command]
        Examples:
            $help
            $help weather
        """
        prefix = ctx.prefix or "$"

        if command_name:
            await self._send_command_detail(ctx, prefix, command_name.strip().lstrip(prefix).lower())
            return

        embed = discord.Embed(
            title="📖 Bot Commands",
            description=f"Prefix: `{prefix}`  ·  Use `{prefix}help <command>` for details on one command.",
            color=discord.Color.blurple(),
        )

        for cog_name, cog in sorted(self.bot.cogs.items()):
            visible = sorted(
                (c for c in cog.get_commands() if not c.hidden),
                key=lambda c: c.name,
            )
            if not visible:
                continue

            lines = "\n".join(
                f"**`{usage_string(prefix, c)}`**\n{c.short_doc or NO_DESCRIPTION}"
                for c in visible
            )
            embed.add_field(name=cog_name, value=lines, inline=False)

        await ctx.send(embed=embed)

    async def _send_command_detail(self, ctx: commands.Context, prefix: str, name: str) -> None:
        """Look up one command by name and show its full docstring as usage help."""
        command = self.bot.get_command(name)

        if command is None or command.hidden:
            await ctx.send(
                f"No command called **{name}** found. Run `{prefix}help` to see everything available."
            )
            return

        embed = discord.Embed(
            title=usage_string(prefix, command),
            description=command.help or NO_DESCRIPTION,
            color=discord.Color.blurple(),
        )
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Help(bot))
