from database_agent import database_agent
from response_agent import analyze_data
from visualization import create_visualization


if __name__ == "__main__":

    question = input("\nAsk Shopit AI: ")

    # -----------------------------------------
    # STEP 1: DATABASE AGENT
    # -----------------------------------------

    database_result = database_agent(question)

    sql = database_result["sql"]
    df = database_result["data"]

    print("\n============================================================")
    print("SQL")
    print("============================================================")

    print(sql)

    print("\n============================================================")
    print("DATA")
    print("============================================================")

    print(df)

    # -----------------------------------------
    # STEP 2: RESPONSE / ANALYTICS AGENT
    # -----------------------------------------

    response = analyze_data(
        question,
        df
    )

    print("\n============================================================")
    print("SHOPIT RESPONSE")
    print("============================================================")

    print("\nAnswer:")
    print(response["answer"])

    print("\nInsights:")

    for insight in response.get("insights", []):
        print("-", insight)

    print("\nVisualization required:")
    print(response.get("visualization_required"))

    print("\nChart type:")
    print(response.get("chart_type"))

    print("\nX column:")
    print(response.get("x_column"))

    print("\nY column:")
    print(response.get("y_column"))

    print("\nChart title:")
    print(response.get("chart_title"))

    # -----------------------------------------
    # STEP 3: CREATE VISUALIZATION
    # -----------------------------------------

    if response.get("visualization_required"):

        print("\n============================================================")
        print("CREATING VISUALIZATION")
        print("============================================================")

        create_visualization(
            df=df,
            chart_type=response.get("chart_type"),
            x_column=response.get("x_column"),
            y_column=response.get("y_column"),
            chart_title=response.get("chart_title")
        )

    else:

        print("\nVisualization is not required.")