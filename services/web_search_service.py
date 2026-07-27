import os
from dotenv import load_dotenv
from tavily import TavilyClient

# ==============================================================================
# LOAD ENVIRONMENT
# ==============================================================================

load_dotenv()

client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

# ==============================================================================
# WEB SEARCH
# ==============================================================================

def search_web(
    query: str,
    max_results: int = 5,
):
    """
    Searches the web for general information.

    Returns:
        [
            {
                "title": "...",
                "content": "...",
                "url": "..."
            }
        ]
    """

    print("\n" + "=" * 80)
    print("WEB SEARCH")
    print("=" * 80)
    print(f"Query : {query}")

    try:

        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=False,
            include_images=False,
            include_raw_content=False,
        )

        results = []

        for item in response.get("results", []):

            title = item.get("title", "").strip()
            content = item.get("content", "").strip()
            url = item.get("url", "").strip()

            # Ignore empty results
            if not content:
                continue

            results.append(
                {
                    "title": title,
                    "content": content,
                    "url": url,
                }
            )

        print(f"SEARCH RESULTS : {len(results)}")

        return results

    except Exception as e:

        print("\nWEB SEARCH FAILED")
        print(e)

        return []