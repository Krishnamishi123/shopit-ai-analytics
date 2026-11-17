
import logging

from sql_generator import generate_sql
from query_executor import execute_sql

logger = logging.getLogger("shopit")


def database_agent(question: str) -> dict:
    """Generate SQL, execute it, and return a consistent result."""

    print("\n" + "=" * 60)
    print("DATABASE AGENT")
    print("=" * 60)

    # Step 1: Generate SQL
    try:
        sql = generate_sql(question)

        if not isinstance(sql, str) or not sql.strip():
            raise ValueError("SQL generator returned an empty query.")

        print("\nGenerated SQL:")
        print(sql)

    except Exception:
        logger.exception("SQL generation failed")
        return {
            "question": question,
            "sql": None,
            "data": None,
            "error": "SQL generation failed."
        }

    # Step 2: Execute SQL
    try:
        df = execute_sql(sql)

        if df is None:
            logger.error("SQL execution returned no DataFrame.")
            return {
                "question": question,
                "sql": sql,
                "data": None,
                "error": "SQL execution failed."
            }

        return {
            "question": question,
            "sql": sql,
            "data": df,
            "error": None
        }

    except Exception:
        logger.exception("Database execution failed")
        return {
            "question": question,
            "sql": sql,
            "data": None,
            "error": "Database execution failed."
        }
