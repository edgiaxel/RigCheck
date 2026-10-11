import logging
from typing import Any, Dict, List, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(
        self,
        api_key: Optional[str] = None,
        enabled: Optional[bool] = None,
        timeout: Optional[float] = None,
    ):
        self.api_key = api_key if api_key is not None else settings.serpapi_api_key
        self.enabled = enabled if enabled is not None else settings.serpapi_enabled
        self.timeout = timeout if timeout is not None else settings.serpapi_timeout_seconds

    async def search_technical_specs(
        self, query: str, max_results: int = 3
    ) -> Optional[Dict[str, Any]]:
        """Query SerpAPI for technical specifications of a component.
        
        Returns parsed snippets and metadata, or None if disabled/failed.
        """
        if not self.enabled or not self.api_key or not self.api_key.strip():
            logger.info("SerpAPI technical search is disabled or missing API key.")
            return None

        clean_query = query.strip()
        if not clean_query:
            return None

        params = {
            "q": clean_query,
            "api_key": self.api_key,
            "engine": "google",
            "num": max_results,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get("https://serpapi.com/search", params=params)

            if response.status_code != 200:
                logger.warning(
                    f"SerpAPI returned non-200 status {response.status_code}: {response.text[:200]}"
                )
                return None

            data = response.json()
            organic_results = data.get("organic_results", [])

            results: List[Dict[str, str]] = []
            for item in organic_results[:max_results]:
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                link = item.get("link", "")
                if snippet or title:
                    results.append({"title": title, "snippet": snippet, "link": link})

            return {
                "query": clean_query,
                "results": results,
                "raw_count": len(results),
            }

        except httpx.TimeoutException:
            logger.warning(f"SerpAPI search timed out after {self.timeout}s for query: {clean_query}")
            return None
        except Exception as exc:
            logger.warning(f"SerpAPI search encountered error: {exc}")
            return None


search_service = SearchService()
