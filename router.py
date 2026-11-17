from query_classifier import classify_query
from rag import ask_shopit_policy

# Change this import/function name to match
# your actual Stage 2 SQL Agent.
from sql_agent import ask_database


def process_query(question):

    # =====================================================
    # STEP 1: CLASSIFY
    # =====================================================

    category = classify_query(question)

    print(
        "\nQuery Category:",
        category
    )


    # =====================================================
    # STEP 2: ROUTE
    # =====================================================

    if category == "RAG":

        answer, sources = ask_shopit_policy(
            question
        )

        return {
            "category": "RAG",
            "answer": answer,
            "sources": sources
        }


    elif category == "DATABASE":

        answer = ask_database(
            question
        )

        return {
            "category": "DATABASE",
            "answer": answer,
            "sources": []
        }


    elif category == "UNKNOWN":

        return {
            "category": "UNKNOWN",
            "answer": (
                "I can currently answer questions "
                "related to Shopit's policies and "
                "business data."
            ),
            "sources": []
        }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    while True:

        question = input(
            "\nAsk Shopit: "
        )

        if question.lower() == "exit":
            break

        result = process_query(
            question
        )

        print("\n==============================")
        print("SHOPIT AI")
        print("==============================")

        print(
            "Category:",
            result["category"]
        )

        print(
            "\nAnswer:"
        )

        print(
            result["answer"]
        )