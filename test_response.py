from database_agent import database_agent
from response_agent import analyze_data


if __name__ == "__main__":
 while(True):
    question = input("\nAsk Shopit AI: ")
    database_result = database_agent(question)
    response = analyze_data(
        question,
        database_result["data"] 
    )

    print("\n============================================================")
    print("SHOPIT RESPONSE")
    print("============================================================")

    print("\nAnswer:")
    print(response["answer"])

    print("\nInsights:")

    for insight in response["insights"]:
        print("-", insight)

    print("\nVisualization required:")
    print(response["visualization_required"])

    print("\nChart type:")
    print(response["chart_type"])

    print("\nChart data:")
    print(response["chart_data"])