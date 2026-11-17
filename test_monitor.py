
from monitoring import run_shopit_query, LOG_PATH


def main():
    question = "What is Shopit's return policy?"

    result = run_shopit_query(question)

    print("Category:", result.get("category"))
    print("Answer:", result.get("answer"))
    print("Log file:", LOG_PATH)


if __name__ == "__main__":
    main()
