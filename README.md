# SteamDB MCP Server

A custom MCP (Model Context Protocol) server for querying **Steam** and **SteamDB-style** data.

## Features

| Tool | Description |
|------|-------------|
| `search_games` | Search Steam store by keyword |
| `get_game_details` | Full app info (price, genres, release date, screenshots, etc.) |
| `get_player_count` | Live concurrent players for any app |
| `get_top_games` | Top games by player count (via SteamSpy) |
| `get_player_history` | 24h peaks + ownership stats (SteamSpy fallback) |
| `get_price_history` | Current Steam price overview |
| `get_wishlist` | Fetch a public Steam wishlist |
| `get_user_library` | Owned games + playtime (requires Steam API key) |
| `get_recent_news` | Latest news articles for an app |

## Setup

### 1. Install dependencies

```bash
uv venv steamdb-mcp
source steamdb-mcp/bin/activate
uv pip install mcp httpx beautifulsoup4
```

Or with `pip`:

```bash
python -m venv steamdb-mcp
source steamdb-mcp/bin/activate
pip install mcp httpx beautifulsoup4
```

### 2. Get a Steam API Key (optional)

Only needed for `get_user_library`. Get one free at:
https://steamcommunity.com/dev/apikey

### 3. Configure MCP client

Add to your MCP config (Claude Desktop, Hermes, etc.):

**Stdio mode (recommended):**

```json
{
  "mcpServers": {
    "steamdb": {
      "command": "/home/USER/steamdb-mcp/bin/python",
      "args": ["/home/USER/steamdb-mcp/server.py"],
      "env": {
        "STEAM_API_KEY": "your_key_here"
      }
    }
  }
}
```

> Replace `/home/USER` with your actual home path.

### 4. Restart your MCP client

The tools will appear automatically.

## Notes

- **SteamDB** itself has no official public API for most data. This server combines:
  - Steam Web API (player counts, news, libraries)
  - Steam Store API (game details, search, prices)
  - SteamSpy API (top charts, ownership estimates, tags)
- Price history uses IsThereAnyDeal (limited without API key).
- Wishlists must be **public** to be readable.

## License

MIT — do whatever you want.
