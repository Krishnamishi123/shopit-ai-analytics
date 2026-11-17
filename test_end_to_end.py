
import csv
import os
from datetime import datetime

from graph import shopit_graph


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_PATH = os.path.join(BASE_DIR, "end_to_end_report.csv")


def run_test(test_name, question, expected_category):
    """Run one question through the complete LangGraph workflow."""

    initial_state = {
        "question": question,
        "category": "",
        "sql": "",
        "data": None,
        "answer": "",
        "insights": [],
        "visualization_required": False,
        "chart_type": None,
        "x_column": None,
        "y_column": None,
        "chart_title": None,
    }

    try:
        result = shopit_graph.invoke(initial_state)

        category = result.get("category", "")
        answer = result.get("answer", "")
        data = result.get("data")

        checks = []

        # Check 1: Was the question routed correctly?
        if category != expected_category:
            checks.append(
                f"Expected {expected_category}, got {category}"
            )

        # Check 2: Did the workflow produce an answer?
        if not isinstance(answer, str) or not answer.strip():
            checks.append("Answer is empty")

        # Check 3: Database questions should return query data.
        if expected_category == "DATABASE" and data is None:
            checks.append("Database returned no DataFrame")

        passed = len(checks) == 0
        details = (
            "All basic checks passed"
            if passed
            else "; ".join(checks)
        )

        # Print useful diagnostics without dumping all customer data.
        print(f"\n{'PASS' if passed else 'FAIL'}: {test_name}")
        print("Question:", question)
        print("Expected category:", expected_category)
        print("Actual category:", category)
        print("Answer preview:", str(answer)[:250])
        print("Details:", details)

        return {
            "test_name": test_name,
            "status": "PASS" if passed else "FAIL",
            "category": category,
            "details": details,
            "tested_at": datetime.now().isoformat(timespec="seconds"),
        }

    except Exception as exc:
        details = f"{type(exc).__name__}: {exc}"

        print(f"\nERROR: {test_name}")
        print("Details:", details)

        return {
            "test_name": test_name,
            "status": "ERROR",
            "category": "",
            "details": details,
            "tested_at": datetime.now().isoformat(timespec="seconds"),
        }


def main():
    # Use clear questions so the intended route is unambiguous.
    test_cases = [
        (
            "Product revenue analytics",
            "Show the top 5 products by revenue",
            "DATABASE",
        ),
        (
            "Customer spending analytics",
            "Which customers have spent the most?",
            "DATABASE",
        ),
        (
            "Return policy retrieval",
            "What is Shopit's return policy?",
            "RAG",
        ),
        (
            "Privacy policy retrieval",
            "What does Shopit's privacy policy say?",
            "RAG",
        ),
        (
            "Unsupported general knowledge",
            "What is the capital of France?",
            "UNKNOWN",
        ),
    ]

    results = []

    print("=" * 55)
    print("SHOPIT END-TO-END TESTS")
    print("=" * 55)
    print("These tests invoke the actual graph and may call the LLM.")

    for name, question, expected_category in test_cases:
        result = run_test(name, question, expected_category)
        results.append(result)

    fieldnames = [
        "test_name",
        "status",
        "category",
        "details",
        "tested_at",
    ]

    with open(REPORT_PATH, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    passed = sum(r["status"] == "PASS" for r in results)
    failed = sum(r["status"] == "FAIL" for r in results)
    errors = sum(r["status"] == "ERROR" for r in results)

    print("\n" + "=" * 55)
    print("FINAL TEST SUMMARY")
    print("=" * 55)
    print(f"Total tests: {len(results)}")
    print(f"Passed:      {passed}")
    print(f"Failed:      {failed}")
    print(f"Errors:      {errors}")
    print(f"Report saved to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
