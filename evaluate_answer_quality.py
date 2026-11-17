
import json
import logging
from pathlib import Path

import pandas as pd

from graph import shopit_graph

BASE_DIR = Path(__file__).resolve().parent
TEST_FILE = BASE_DIR / "quality_test_cases.json"
REPORT_FILE = BASE_DIR / "quality_evaluation_report.csv"

logging.basicConfig(level=logging.INFO)


def run_test(test_case):
    question = test_case["question"]
    expected_category = test_case["expected_category"]

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
        "chart_title": None
    }

    try:
        result = shopit_graph.invoke(initial_state)

        actual_category = result.get("category", "")
        answer = result.get("answer", "")

        category_pass = actual_category == expected_category
        answer_pass = isinstance(answer, str) and bool(answer.strip())

        required_terms = test_case.get("must_contain", [])
        missing_terms = [
            term for term in required_terms
            if term.casefold() not in answer.casefold()
        ]
        keyword_pass = len(missing_terms) == 0

        # This is a structural check, not proof of factual correctness.
        data_pass = (
            actual_category != "DATABASE"
            or result.get("data") is not None
        )

        passed = (
            category_pass
            and answer_pass
            and keyword_pass
            and data_pass
        )

        return {
            "test_id": test_case["id"],
            "question": question,
            "expected_category": expected_category,
            "actual_category": actual_category,
            "category_pass": category_pass,
            "answer_pass": answer_pass,
            "keyword_pass": keyword_pass,
            "data_pass": data_pass,
            "missing_terms": ", ".join(missing_terms),
            "passed": passed,
            "answer": answer
        }

    except Exception as exc:
        logging.exception("Evaluation failed for %s", test_case["id"])

        return {
            "test_id": test_case["id"],
            "question": question,
            "expected_category": expected_category,
            "actual_category": "ERROR",
            "category_pass": False,
            "answer_pass": False,
            "keyword_pass": False,
            "data_pass": False,
            "missing_terms": "",
            "passed": False,
            "answer": f"Evaluation error: {type(exc).__name__}"
        }


def main():
    with open(TEST_FILE, "r", encoding="utf-8") as file:
        test_cases = json.load(file)

    results = [run_test(test) for test in test_cases]
    report = pd.DataFrame(results)
    report.to_csv(REPORT_FILE, index=False)

    total = len(results)
    passed = sum(row["passed"] for row in results)

    print("\n" + "=" * 50)
    print("SHOPIT ANSWER-QUALITY EVALUATION")
    print("=" * 50)
    print(f"Tests run: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Pass rate: {passed / total * 100:.1f}%")
    print(f"Report saved to: {REPORT_FILE}")

    print("\nFailed tests:")
    for row in results:
        if not row["passed"]:
            print(
                f"- {row['test_id']}: {row['question']} "
                f"(category={row['actual_category']})"
            )


if __name__ == "__main__":
    main()
