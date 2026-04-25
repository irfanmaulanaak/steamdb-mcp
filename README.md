# SteamDB MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for querying **Steam** and **SteamDB-style** data. Search games, check live player counts, view price info, browse top charts, and more — all from your AI assistant.

[![PyPI](https://img.shields.io/badge/pypi-steamdb--mcp-blue)](https://pypi.org/project/steamdb-mcp/)
[![GitHub](https://img.shields.io/badge/github-irfanmaulanaak%2Fsteamdb--mcp-black)](https://github.com/irfanmaulanaak/steamdb-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✅ Features

| Tool | Description |
|------|-------------|
| `search_games` | Search the Steam store by keyword |
| `get_game_details` | Full app info: price, genres, release date, screenshots, etc. |
| `get_player_count` | Live concurrent players for any Steam app |
| `get_top_games` | Top games by current player count |
| `get_player_history` | 24h peaks + ownership stats |
| `get_price_history` | Current Steam price overview |
| `get_wishlist` | Fetch a public Steam wishlist |
| `get_user_library` | Owned games + playtime (**requires Steam API key**) |
| `get_recent_news` | Latest news articles for a game |

## 🚀 Quick Start

### Option 1: uvx (recommended — fastest, no install)

```bash
# Run directly without installing
uvx steamdb-mcp
```

### Option 2: pip install

```bash
pip install steamdb-mcp
steamdb-mcp
```

### Option 3: From source

```bash
git clone https://github.com/irfanmaulanaak/steamdb-mcp.git
cd steamdb-mcp
uv pip install -e .
steamdb-mcp
```

## ⚙️ MCP Client Configuration

Add to your MCP client config (Claude Desktop, Hermes, Cursor, etc.):

### Using uvx (recommended)

```json
{
  "mcpServers": {
    "steamdb": {
      "command": "uvx",
      "args": ["steamdb-mcp"]
    }
  }
}
```

### Using pip

```json
{
  "mcpServers": {
    "steamdb": {
      "command": "steamdb-mcp"
    }
  }
}
```

### With Steam API Key (optional)

Only needed for `get_user_library`:

```json
{
  "mcpServers": {
    "steamdb": {
      "command": "uvx",
      "args": ["steamdb-mcp"],
      "env": {
        "STEAM_API_KEY": "your_steam_api_key_here"
      }
    }
  }
}
```

Get a free Steam API key at: https://steamcommunity.com/dev/apikey

## 📜 Hermes Agent Config

For [Hermes Agent](https://github.com/hermes) users, add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  steamdb:
    command: "uvx"
    args: ["steamdb-mcp"]
    env:
      STEAM_API_KEY: ""
```

## 🔧 Example Usage

Once connected, ask your AI assistant things like:

- *"Search for Forza Horizon 6 on Steam"*
- *"How many players are currently playing Elden Ring?"*
- *"What's the price of Crimson Desert?"*
- *"Show me the top 10 games on Steam right now"*
- *"Get recent news for Counter-Strike 2"*

## 📦 Data Sources

This server combines multiple public APIs:
- **Steam Web API** — player counts, news, user libraries
- **Steam Store API** — game details, search, prices
- **SteamSpy** — top charts, ownership estimates, tags

> Note: SteamDB itself does not have an official public API. This server provides SteamDB-*style* data by aggregating the above sources.

## 📝 Requirements

- Python 3.10+
- (Optional) A Steam Web API key for `get_user_library`

## 📄 License

MIT — see [LICENSE](LICENSE)

## 👍 Contributing

Issues and PRs welcome! https://github.com/irfanmaulanaak/steamdb-mcp/issues
