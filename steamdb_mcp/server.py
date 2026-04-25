#!/usr/bin/env python3
"""
SteamDB MCP Server
Provides tools for querying Steam/SteamDB data:
- Game search & details
- Player counts & history
- Price tracking
- Top charts
"""

import os
import json
import asyncio
from typing import Any, Optional
from datetime import datetime

import httpx
from mcp.server import Server
from mcp.types import TextContent, Tool

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
STEAM_API_KEY = os.environ.get("STEAM_API_KEY", "")
app = Server("steamdb-mcp")

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------
async def fetch_json(url: str, params: Optional[dict] = None, headers: Optional[dict] = None) -> dict:
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        return resp.json()

async def fetch_text(url: str, params: Optional[dict] = None, headers: Optional[dict] = None) -> str:
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        return resp.text

# ---------------------------------------------------------------------------
# Tools definition
# ---------------------------------------------------------------------------
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_games",
            description="Search Steam store for games by keyword",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keyword"},
                    "count": {"type": "integer", "default": 10, "description": "Max results"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_game_details",
            description="Get detailed info for a Steam app by its AppID",
            inputSchema={
                "type": "object",
                "properties": {
                    "appid": {"type": "integer", "description": "Steam AppID"}
                },
                "required": ["appid"]
            }
        ),
        Tool(
            name="get_player_count",
            description="Get current concurrent players for a Steam app",
            inputSchema={
                "type": "object",
                "properties": {
                    "appid": {"type": "integer", "description": "Steam AppID"}
                },
                "required": ["appid"]
            }
        ),
        Tool(
            name="get_top_games",
            description="Get top Steam games by current player count",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20, "description": "Number of top games"}
                }
            }
        ),
        Tool(
            name="get_player_history",
            description="Get 24h player peak & history summary for an app (via SteamDB-style data)",
            inputSchema={
                "type": "object",
                "properties": {
                    "appid": {"type": "integer", "description": "Steam AppID"}
                },
                "required": ["appid"]
            }
        ),
        Tool(
            name="get_price_history",
            description="Get price history for a game via IsThereAnyDeal (requires ITAD API key or uses limited public data)",
            inputSchema={
                "type": "object",
                "properties": {
                    "appid": {"type": "integer", "description": "Steam AppID"},
                    "region": {"type": "string", "default": "us", "description": "Region code"}
                },
                "required": ["appid"]
            }
        ),
        Tool(
            name="get_wishlist",
            description="Get a Steam user's wishlist (public only)",
            inputSchema={
                "type": "object",
                "properties": {
                    "steamid": {"type": "string", "description": "SteamID64 of the user"}
                },
                "required": ["steamid"]
            }
        ),
        Tool(
            name="get_user_library",
            description="Get a Steam user's owned games (requires STEAM_API_KEY env var)",
            inputSchema={
                "type": "object",
                "properties": {
                    "steamid": {"type": "string", "description": "SteamID64 of the user"}
                },
                "required": ["steamid"]
            }
        ),
        Tool(
            name="get_recent_news",
            description="Get recent news articles for a Steam app",
            inputSchema={
                "type": "object",
                "properties": {
                    "appid": {"type": "integer", "description": "Steam AppID"},
                    "count": {"type": "integer", "default": 5, "description": "Number of articles"}
                },
                "required": ["appid"]
            }
        ),
    ]

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "search_games":
        return await _search_games(arguments)
    elif name == "get_game_details":
        return await _get_game_details(arguments)
    elif name == "get_player_count":
        return await _get_player_count(arguments)
    elif name == "get_top_games":
        return await _get_top_games(arguments)
    elif name == "get_player_history":
        return await _get_player_history(arguments)
    elif name == "get_price_history":
        return await _get_price_history(arguments)
    elif name == "get_wishlist":
        return await _get_wishlist(arguments)
    elif name == "get_user_library":
        return await _get_user_library(arguments)
    elif name == "get_recent_news":
        return await _get_recent_news(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def _search_games(args: dict) -> list[TextContent]:
    query = args["query"]
    count = args.get("count", 10)
    url = "https://store.steampowered.com/api/storesearch/"
    params = {"term": query, "cc": "US", "l": "en", "v": 1}
    data = await fetch_json(url, params)
    items = data.get("items", [])[:count]
    results = []
    for item in items:
        results.append({
            "appid": item.get("id"),
            "name": item.get("name"),
            "price": item.get("price", {}).get("final_formatted", "N/A"),
            "released": item.get("released", "?"),
            "tiny_image": item.get("tiny_image", "")
        })
    return [TextContent(type="text", text=json.dumps(results, indent=2))]

async def _get_game_details(args: dict) -> list[TextContent]:
    appid = args["appid"]
    url = f"https://store.steampowered.com/api/appdetails"
    params = {"appids": appid, "cc": "US", "l": "en"}
    data = await fetch_json(url, params)
    app_data = data.get(str(appid), {})
    if not app_data.get("success"):
        return [TextContent(type="text", text=json.dumps({"error": "App not found or data unavailable"}, indent=2))]
    d = app_data.get("data", {})
    result = {
        "appid": appid,
        "name": d.get("name"),
        "type": d.get("type"),
        "short_description": d.get("short_description", ""),
        "developers": d.get("developers", []),
        "publishers": d.get("publishers", []),
        "release_date": d.get("release_date", {}).get("date"),
        "coming_soon": d.get("release_date", {}).get("coming_soon"),
        "price_overview": d.get("price_overview"),
        "metacritic": d.get("metacritic", {}).get("score"),
        "genres": [g["description"] for g in d.get("genres", [])],
        "categories": [c["description"] for c in d.get("categories", [])],
        "header_image": d.get("header_image"),
        "website": d.get("website"),
        "required_age": d.get("required_age"),
        "is_free": d.get("is_free"),
        "platforms": d.get("platforms"),
        "screenshots_count": len(d.get("screenshots", [])),
        "movies_count": len(d.get("movies", [])),
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def _get_player_count(args: dict) -> list[TextContent]:
    appid = args["appid"]
    url = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
    data = await fetch_json(url, {"appid": appid})
    response = data.get("response", {})
    result = {
        "appid": appid,
        "player_count": response.get("player_count"),
        "result": response.get("result")
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def _get_top_games(args: dict) -> list[TextContent]:
    limit = args.get("limit", 20)
    url = "https://api.steampowered.com/ISteamChartsService/GetGamesByPlayerCount/v1/"
    # Steam Charts API may not be public; fallback to SteamSpy top 100
    url2 = "https://steamspy.com/api.php"
    params = {"request": "top100in2weeks"}
    data = await fetch_json(url2, params)
    results = []
    for appid, info in list(data.items())[:limit]:
        results.append({
            "appid": int(appid),
            "name": info.get("name"),
            "average_2weeks": info.get("average_2weeks"),
            "median_2weeks": info.get("median_2weeks"),
            "ccu": info.get("ccu"),
            "developer": info.get("developer"),
            "publisher": info.get("publisher"),
            "price": info.get("price"),
            "discount": info.get("discount"),
            "tags": list(info.get("tags", {}).keys())[:5]
        })
    return [TextContent(type="text", text=json.dumps(results, indent=2))]

async def _get_player_history(args: dict) -> list[TextContent]:
    appid = args["appid"]
    # SteamDB itself doesn't have a public API for this, but Steam Charts web has data
    # We'll use SteamSpy for ownership/playtime estimates and try SteamDB web
    url = f"https://steamdb.info/api/GetGraph/?type=concurrent_max&appid={appid}"
    result = {"appid": appid}
    try:
        data = await fetch_json(url)
        result["steamdb_graph_data"] = data
    except Exception as e:
        result["steamdb_graph_error"] = str(e)
    # Also get SteamSpy data
    try:
        spy = await fetch_json("https://steamspy.com/api.php", {"request": "appdetails", "appid": appid})
        result["steamspy"] = {
            "owners": spy.get("owners"),
            "average_playtime": spy.get("average_forever"),
            "median_playtime": spy.get("median_forever"),
            "ccu": spy.get("ccu"),
            "tags": list(spy.get("tags", {}).keys())[:10]
        }
    except Exception as e:
        result["steamspy_error"] = str(e)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def _get_price_history(args: dict) -> list[TextContent]:
    appid = args["appid"]
    region = args.get("region", "us")
    # IsThereAnyDeal has a public endpoint for current prices; history requires API key
    url = f"https://api.isthereanydeal.com/games/lookup/v1"
    params = {"key": "", "appid": appid}  # empty key triggers limited access
    result = {"appid": appid, "note": "Full history requires ITAD API key. Showing current overview."}
    # Fallback to Steam store price
    try:
        steam = await fetch_json("https://store.steampowered.com/api/appdetails", {"appids": appid, "cc": region.upper(), "l": "en"})
        if not isinstance(steam, dict):
            result["steam_price_error"] = f"Unexpected response type: {type(steam).__name__}"
        else:
            app_data = steam.get(str(appid), {})
            if isinstance(app_data, list):
                result["steam_price_error"] = "Unexpected app_data type: list"
            elif isinstance(app_data, dict) and app_data.get("success"):
                d = app_data.get("data", {})
                if isinstance(d, dict):
                    result["steam_price"] = d.get("price_overview")
                    result["is_free"] = d.get("is_free", False)
                    if d.get("is_free"):
                        result["steam_price_note"] = "Game is free-to-play"
                else:
                    result["steam_price_error"] = f"Unexpected data type: {type(d).__name__}"
            else:
                result["steam_price_error"] = "App data unavailable or app not found"
    except Exception as e:
        result["steam_price_error"] = str(e)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def _get_wishlist(args: dict) -> list[TextContent]:
    steamid = args["steamid"]
    url = f"https://store.steampowered.com/wishlist/profiles/{steamid}/wishlistdata/"
    params = {"v": 1}
    try:
        data = await fetch_json(url, params)
        items = []
        for appid, item in data.items():
            items.append({
                "appid": int(appid),
                "name": item.get("name"),
                "priority": item.get("priority", 0),
                "added": datetime.fromtimestamp(item.get("added", 0)).isoformat() if item.get("added") else None,
                "subs": [{"packageid": s[0], "price": s[1]} for s in item.get("subs", [])]
            })
        return [TextContent(type="text", text=json.dumps({"count": len(items), "items": items}, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e), "note": "Wishlist may be private"}, indent=2))]

async def _get_user_library(args: dict) -> list[TextContent]:
    steamid = args["steamid"]
    if not STEAM_API_KEY:
        return [TextContent(type="text", text=json.dumps({"error": "STEAM_API_KEY environment variable not set"}, indent=2))]
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {"key": STEAM_API_KEY, "steamid": steamid, "include_appinfo": 1, "include_played_free_games": 1}
    data = await fetch_json(url, params)
    games = data.get("response", {}).get("games", [])
    result = {
        "game_count": data.get("response", {}).get("game_count", len(games)),
        "games": sorted([
            {
                "appid": g["appid"],
                "name": g.get("name"),
                "playtime_forever": g.get("playtime_forever"),
                "playtime_2weeks": g.get("playtime_2weeks"),
                "img_icon_url": g.get("img_icon_url")
            }
            for g in games
        ], key=lambda x: x["playtime_forever"], reverse=True)[:100]
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def _get_recent_news(args: dict) -> list[TextContent]:
    appid = args["appid"]
    count = args.get("count", 5)
    url = f"https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"
    params = {"appid": appid, "count": count, "maxlength": 500, "format": "json"}
    data = await fetch_json(url, params)
    items = data.get("appnews", {}).get("newsitems", [])
    results = []
    for item in items:
        results.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "author": item.get("author"),
            "date": datetime.fromtimestamp(item.get("date", 0)).isoformat() if item.get("date") else None,
            "feedlabel": item.get("feedlabel"),
            "contents": item.get("contents", "")[:400] + "..." if len(item.get("contents", "")) > 400 else item.get("contents", "")
        })
    return [TextContent(type="text", text=json.dumps(results, indent=2))]

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
async def _async_main():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

def main():
    asyncio.run(_async_main())

if __name__ == "__main__":
    main()
