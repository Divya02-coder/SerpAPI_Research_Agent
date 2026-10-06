import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from serpapi import GoogleSearch


load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")


def _search_serpapi(params):
    """
    Execute a SerpApi request.
    """

    if not SERPAPI_API_KEY:
        raise ValueError(
            "SERPAPI_API_KEY is missing from .env"
        )

    params = params.copy()
    params["api_key"] = SERPAPI_API_KEY

    try:
        search = GoogleSearch(params)
        return search.get_dict()

    except Exception as e:
        return {
            "error": str(e)
        }


def _get_domain(url):
    """
    Extract domain from a URL.
    """

    try:
        return urlparse(url).netloc.replace("www.", "")

    except Exception:
        return ""


def web_search(query):
    """
    Search the live web using Google through SerpApi.
    """

    print("🔎 WEB SEARCH")
    print(f"   {query}")

    data = _search_serpapi({
        "engine": "google",
        "q": query,
        "num": 7,
        "hl": "en",
        "gl": "in"
    })

    # ---------------------------------------------
    # Handle SerpApi error
    # ---------------------------------------------

    if "error" in data:

        return {
            "search_type": "web",
            "query": query,
            "source_count": 0,
            "sources": [],
            "error": data["error"]
        }

    # ---------------------------------------------
    # Extract organic results
    # ---------------------------------------------

    sources = []

    for result in data.get("organic_results", []):

        url = result.get("link", "")

        if not url:
            continue

        sources.append({
            "title": result.get("title", ""),
            "url": url,
            "domain": _get_domain(url),
            "snippet": result.get("snippet", "")
        })

    return {
        "search_type": "web",
        "query": query,
        "source_count": len(sources),
        "sources": sources
    }


def news_search(query):
    """
    Search current/recent news using SerpApi.
    """

    print("📰 NEWS SEARCH")
    print(f"   {query}")

    data = _search_serpapi({
        "engine": "google_news",
        "q": query,
        "hl": "en",
        "gl": "in"
    })

    # ---------------------------------------------
    # Handle SerpApi error
    # ---------------------------------------------

    if "error" in data:

        return {
            "search_type": "news",
            "query": query,
            "source_count": 0,
            "sources": [],
            "error": data["error"]
        }

    # ---------------------------------------------
    # Extract news results
    # ---------------------------------------------

    sources = []

    for result in data.get("news_results", []):

        url = result.get("link", "")

        if not url:
            continue

        source_info = result.get("source", {})

        sources.append({
            "title": result.get("title", ""),
            "url": url,
            "domain": _get_domain(url),
            "publisher": source_info.get("name", ""),
            "date": result.get("date", ""),
            "snippet": result.get("snippet", "")
        })

    return {
        "search_type": "news",
        "query": query,
        "source_count": len(sources),
        "sources": sources
    }


# =====================================================
# GEMINI TOOL SCHEMAS
# =====================================================

TOOL_SCHEMAS = [

    {
        "type": "function",
        "name": "web_search",
        "description": (
            "Search the live web for factual, technical, "
            "comparative, research, or current information."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "A focused web search query."
                    )
                }
            },
            "required": ["query"]
        }
    },

    {
        "type": "function",
        "name": "news_search",
        "description": (
            "Search current and recent news for breaking events, "
            "latest developments, recent announcements, "
            "or current affairs."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "A focused news search query."
                    )
                }
            },
            "required": ["query"]
        }
    }
]


TOOL_FUNCTIONS = {
    "web_search": web_search,
    "news_search": news_search
}