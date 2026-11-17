
import os
import re
import sqlite3
from urllib.parse import quote

import pandas as pd


# Always locate the database relative to this Python file.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "shopit.db")


def get_connection():
    """Open the existing Shopit database in read-only mode."""

    if not os.path.isfile(DATABASE_PATH):
        raise FileNotFoundError(
            f"Shopit database not found: {DATABASE_PATH}"
        )

    # SQLite URI paths should use forward slashes.
    db_path = os.path.abspath(DATABASE_PATH).replace("\\", "/")
    db_uri = f"file:{quote(db_path, safe='/:')}?mode=ro"

    conn = sqlite3.connect(db_uri, uri=True, timeout=10)

    # Additional protection against writes through this connection.
    conn.execute("PRAGMA query_only = ON")

    return conn


def validate_sql(sql: str):
    """Perform basic validation before SQLite executes the query."""

    if not isinstance(sql, str) or not sql.strip():
        return False, "SQL query is empty."

    if len(sql) > 20000:
        return False, "SQL query exceeds the maximum allowed length."

    cleaned = sql.strip()

    # Remove Markdown fences if the model accidentally included them.
    cleaned = re.sub(
        r"\A```(?:sql)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s*```\s*\Z", "", cleaned)

    # Remove comments for this basic validation step.
    cleaned = re.sub(
        r"/\*.*?\*/|--[^\r\n]*",
        " ",
        cleaned,
        flags=re.DOTALL,
    ).strip()

    # Permit one optional trailing semicolon only.
    cleaned = cleaned.rstrip()

    if cleaned.endswith(";"):
        cleaned = cleaned[:-1].rstrip()

    if not cleaned:
        return False, "SQL query is empty."

    # Reject additional statements.
    if ";" in cleaned:
        return False, "Multiple SQL statements are not allowed."

    # Only SELECT queries and read-only CTEs are accepted.
    if not re.match(r"^(SELECT|WITH)\b", cleaned, re.IGNORECASE):
        return False, "Only SELECT queries are allowed."

    # Basic early rejection. SQLite's authorizer below provides
    # the stronger enforcement and is not dependent on this regex.
    forbidden = re.compile(
        r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|"
        r"ATTACH|DETACH|VACUUM|REINDEX|PRAGMA|BEGIN|COMMIT|"
        r"ROLLBACK|SAVEPOINT|RELEASE|GRANT|REVOKE|EXEC|EXECUTE)\b",
        re.IGNORECASE,
    )

    if forbidden.search(cleaned):
        return False, "Prohibited SQL operation detected."

    return True, cleaned


def _read_only_authorizer(action, arg1, arg2, database, source):
    """
    Permit ordinary reads, SELECTs, functions and recursive CTEs.
    Deny all other SQLite operations.
    """

    allowed_actions = {
        sqlite3.SQLITE_SELECT,
        sqlite3.SQLITE_READ,
        sqlite3.SQLITE_FUNCTION,
    }

    # Some Python/SQLite builds expose this action constant.
    if hasattr(sqlite3, "SQLITE_RECURSIVE"):
        allowed_actions.add(sqlite3.SQLITE_RECURSIVE)

    if action in allowed_actions:
        return sqlite3.SQLITE_OK

    return sqlite3.SQLITE_DENY


def execute_sql(sql):
    """Validate and execute a read-only query, returning a DataFrame."""

    conn = None

    try:
        allowed, validated_sql = validate_sql(sql)

        if not allowed:
            print("SQL rejected:", validated_sql)
            return None

        conn = get_connection()

        # Enforce read-only behavior at SQLite's operation level.
        conn.set_authorizer(_read_only_authorizer)

        print("\n" + "=" * 55)
        print("EXECUTING VALIDATED READ-ONLY SQL")
        print("=" * 55)
        print(validated_sql)

        df = pd.read_sql_query(validated_sql, conn)

        print("\nQuery executed successfully.")
        print(f"Rows returned: {len(df)}")
        print(f"Columns returned: {list(df.columns)}")

        return df

    except Exception as exc:
        print(
            f"SQL execution error: {type(exc).__name__}: {exc}"
        )
        return None

    finally:
        if conn is not None:
            conn.close()
