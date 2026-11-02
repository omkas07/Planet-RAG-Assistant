from langchain_core.tools import tool
from ingest import Ingest
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv("MYSQL_URL"), pool_pre_ping=True)

class Tools():
    @staticmethod
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

    @staticmethod
    @tool
    def list_tables():
        """Lists all tables in the MySQL database. Call this first to see what data is available."""
        try:
            tables = inspect(engine).get_table_names()
        except Exception as e:
            return f"Database connection error: {e}"
        return ", ".join(tables) if tables else "No tables found."

    @staticmethod
    @tool
    def describe_table(table_name: str) -> str:
        """Shows the columns and their types for a MySQL table. Call this before writing
        a query to get the exact column names."""
        try:
            insp = inspect(engine)
            if table_name not in insp.get_table_names():
                return f"Error: table '{table_name}' does not exist."
            columns = insp.get_columns(table_name)
        except Exception as e:
            return f"Database connection error: {e}"
        return "\n".join(f"{c['name']} ({c['type']})" for c in columns)