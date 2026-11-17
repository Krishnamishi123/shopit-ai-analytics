
import csv
import os
from datetime import datetime

from query_executor import validate_sql, execute_sql


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_PATH = os.path.join(BASE_DIR, "evaluation_report.csv")


def run_test(name, test_function):
    """Run one test and store its result."""
    try:
        passed, details = test_function()
        status = "PASS" if passed else "FAIL"
    except Exception as exc:
        status = "ERROR"
        details = f"{type(exc).__name__}: {exc}"

    result = {
        "test_name": name,
        "status": status,
        "details": str(details),
        "tested_at": datetime.now().isoformat(timespec="seconds"),
    }

    print(f"[{status}] {name}: {details}")
    return result


def test_valid_select():
    allowed, result = validate_sql("SELECT 1 AS test_value")
    return allowed, result


def test_valid_cte():
    sql = "WITH sample AS (SELECT 1 AS value) SELECT value FROM sample"
    allowed, result = validate_sql(sql)
    return allowed, result


def test_block_delete():
    allowed, result = validate_sql("DELETE FROM customers")
    return not allowed, result


def test_block_drop():
    allowed, result = validate_sql("DROP TABLE customers")
    return not allowed, result


def test_block_update():
    allowed, result = validate_sql(
        "UPDATE customers SET customer_id = 0"
    )
    return not allowed, result


def test_block_multiple_statements():
    sql = "SELECT 1; SELECT 2"
    allowed, result = validate_sql(sql)
    return not allowed, result


def test_empty_query():
    allowed, result = validate_sql("")
    return not allowed, result


def test_database_connection():
    # Tests the actual configured SQLite database.
    df = execute_sql("SELECT 1 AS health_check")

    if df is None:
        return False, "Database query failed."

    if df.empty:
        return False, "Health check returned no rows."

    value = df.iloc[0]["health_check"]

    return value == 1, f"Health check returned {value}"


def main():
    print("\n" + "=" * 55)
    print("SHOPIT AI ANALYTICS - EVALUATION")
    print("=" * 55)

    tests = [
        ("Valid SELECT allowed", test_valid_select),
        ("Valid read-only CTE allowed", test_valid_cte),
        ("DELETE rejected", test_block_delete),
        ("DROP rejected", test_block_drop),
        ("UPDATE rejected", test_block_update),
        ("Multiple statements rejected", test_block_multiple_statements),
        ("Empty SQL rejected", test_empty_query),
        ("Database health check", test_database_connection),
    ]

    results = [run_test(name, fn) for name, fn in tests]

    with open(REPORT_PATH, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "test_name",
                "status",
                "details",
                "tested_at",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    passed = sum(r["status"] == "PASS" for r in results)
    failed = sum(r["status"] == "FAIL" for r in results)
    errors = sum(r["status"] == "ERROR" for r in results)

    print("\n" + "=" * 55)
    print(f"Total tests: {len(results)}")
    print(f"Passed:      {passed}")
    print(f"Failed:      {failed}")
    print(f"Errors:      {errors}")
    print(f"Report:      {REPORT_PATH}")
    print("=" * 55)


if __name__ == "__main__":
    main()
