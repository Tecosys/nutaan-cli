import requests
from langchain_core.tools import BaseTool
from pydantic import Field


class BraveWebSearchTool(BaseTool):
    """Brave Search API tool for web searches."""
    
    name: str = "brave_web_search"
    description: str = (
        "Search the web for current information and real-time data. "
        "Use this when you need to find recent news, current events, "
        "or any information that might not be in your training data. "
        "Input should be a clear search query."
    )
    api_token: str = Field(default="BSAzFTVZtJfGuFmmhHgxrM67UZgoOHS")
    
    def _run(self, query: str) -> str:
        try:
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "x-subscription-token": self.api_token
            }
            
            params = {"q": query, "count": 3}
            
            response = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            results = []
            web_results = data.get("web", {}).get("results", [])
            
            for i, result in enumerate(web_results[:3], 1):
                title = result.get("title", "No title")
                description = result.get("description", "No description")
                url = result.get("url", "")
                results.append(f"{i}. {title}\n   {description}\n   URL: {url}")
            
            return "\n\n".join(results) if results else "No results found."
            
        except Exception as e:
            return f"Search error: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)
