from database_agent import database_agent


if __name__ == "__main__":
 while(True):

    question = input("\nAsk Shopit AI: ")

    result = database_agent(question)

    print("\n============================================================")
    print("FINAL DATABASE RESULT")
    print("============================================================")

    print("\nQUESTION:")
    print(result["question"])

    print("\nSQL:")
    print(result["sql"])

    print("\nDATA:")
    print(result["data"])