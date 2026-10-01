# discord_bot

Run `$help` in Discord for a full list of commands.

## Environment variables

| Variable | Required | Description |
| --- | --- | --- |
| `TOKEN` | Yes | Discord bot token. |
| `COK_AUDIO` | No | Override path to the `$cok` countdown audio file. |
| `MC_SERVER_ADDRESS` | No | Minecraft server address (e.g. `play.example.com` or `play.example.com:25566`) for `$mcstatus` and the automatic status alerts. |
| `MC_STATUS_CHANNEL_ID` | No | Discord channel ID where automatic join/leave/online/offline alerts are posted. Requires `MC_SERVER_ADDRESS` to also be set. |
| `MC_STATUS_INTERVAL_MINUTES` | No | How often (in minutes) to poll the Minecraft server for automatic alerts. Defaults to `2`. |

