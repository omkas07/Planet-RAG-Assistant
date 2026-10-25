from langchain_core.tools import tool
from ingest import Ingest

@tool
def search_planets(query: str):
    """Searches the knowledge base about Solar System planets and their moons:
    physical characteristics, orbits, atmospheres, moons, discovery history,
    and space missions. Takes a short search query.
    """
    ingest = Ingest()
    ingest.indexing()
    result = ingest.semantic_search(query)
    return "\n\n".join(
        f"[{i+1}] (source: {c.metadata['source']})\n{c.page_content}"
        for i, c in enumerate(result)
    )

tools = [search_planets]