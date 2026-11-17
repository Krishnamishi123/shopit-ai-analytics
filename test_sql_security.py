
import sqlite3

from query_executor import execute_sql, DATABASE_PATH


def main():
    # A legitimate read query should work.
    df = execute_sql("SELECT 1 AS test_value")

    assert df is not None, "A basic SELECT query failed."
    assert df.iloc[0]["test_value"] == 1
    print("PASS: Read-only SELECT works.")

    # Destructive statements should be rejected.
    assert execute_sql("DELETE FROM customers") is None
    assert execute_sql("DROP TABLE customers") is None
    print("PASS: Destructive SQL is rejected.")

    # Verify the customers table still exists.
    conn = sqlite3.connect(
        f"file:{DATABASE_PATH.replace(chr(92), '/')}?mode=ro",
        uri=True,
    )

    try:
        result = conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name = 'customers'
            """
        ).fetchone()

        assert result is not None, "Customers table is missing."
        print("PASS: Customers table still exists.")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
