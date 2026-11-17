from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from query_classifier import classify_query
from rag import ask_shopit_policy
from sql_agent import ask_database
from database_agent import database_agent
from response_agent import analyze_data
# ============================================================
# STATE
# ============================================================

from typing import TypedDict, Any

class ShopitState(TypedDict):
    question: str
    category: str

    # SQL information
    sql: str
    data: Any

    # Final response
    answer: str
    insights: list

    # Visualization
    visualization_required: bool
    chart_type: str
    x_column: str
    y_column: str
    chart_title: str

# ============================================================
# CLASSIFIER NODE
# ============================================================

def classifier_node(state: ShopitState):

    question = state["question"]

    category = classify_query(question)

    print("\n==============================")
    print("QUERY CLASSIFIER")
    print("==============================")
    print("Question:", question)
    print("Category:", category)

    return {
        "category": category
    }


# ============================================================
# DATABASE NODE
# ============================================================


def database_node(state: ShopitState):
    question = state["question"]

    print("\n" + "=" * 60)
    print("DATABASE BRANCH")
    print("=" * 60)

    database_result = database_agent(question)

    sql = database_result.get("sql")
    data = database_result.get("data")
    error = database_result.get("error")

    if error:
        response = {
            "answer": (
                "I couldn't retrieve the requested business data. "
                "Please try again or rephrase your question."
            ),
            "insights": [],
            "visualization_required": False,
            "chart_type": None,
            "x_column": None,
            "y_column": None,
            "chart_title": None
        }
    else:
        try:
            response = analyze_data(question, data)
        except Exception:
            import logging
            logging.getLogger("shopit").exception(
                "Analytics response generation failed"
            )

            response = {
                "answer": (
                    "I retrieved the data, but couldn't generate "
                    "the business analysis. Please try again."
                ),
                "insights": [],
                "visualization_required": False,
                "chart_type": None,
                "x_column": None,
                "y_column": None,
                "chart_title": None
            }

    return {
        "sql": sql or "",
        "data": data,
        "answer": response["answer"],
        "insights": response["insights"],
        "visualization_required": response["visualization_required"],
        "chart_type": response["chart_type"],
        "x_column": response["x_column"],
        "y_column": response["y_column"],
        "chart_title": response["chart_title"]
    }



# ============================================================
# RAG NODE
# ============================================================

def rag_node(state: ShopitState):

    question = state["question"]

    print("\n==============================")
    print("RAG AGENT")
    print("==============================")

    answer, sources = ask_shopit_policy(question)

    return {
        "answer": answer
    }


# ============================================================
# UNKNOWN NODE
# ============================================================

def unknown_node(state: ShopitState):

    return {
        "answer": (
            "I can currently answer questions related to "
            "Shopit's business data and company policies."
        )
    }


# ============================================================
# ROUTING FUNCTION
# ============================================================

def route_query(state: ShopitState):

    category = state["category"]

    if category == "DATABASE":
        return "database"

    elif category == "RAG":
        return "rag"

    else:
        return "unknown"


# ============================================================
# BUILD GRAPH
# ============================================================

builder = StateGraph(ShopitState)


# Add nodes
builder.add_node("classifier", classifier_node)
builder.add_node("database", database_node)
builder.add_node("rag", rag_node)
builder.add_node("unknown", unknown_node)


# START → CLASSIFIER
builder.add_edge(START, "classifier")


# CLASSIFIER → appropriate branch
builder.add_conditional_edges(
    "classifier",
    route_query,
    {
        "database": "database",
        "rag": "rag",
        "unknown": "unknown"
    }
)


# All branches → END
builder.add_edge("database", END)
builder.add_edge("rag", END)
builder.add_edge("unknown", END)


# Compile
shopit_graph = builder.compile()


# ============================================================
# RUN GRAPH
# ============================================================

if __name__ == "__main__":

    question = input("\nAsk Shopit AI: ")

    result = shopit_graph.invoke({
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
    })

    print("\n========================================")
    print("SHOPIT AI")
    print("========================================")

    print("\nCategory:")
    print(result["category"])

    print("\nAnswer:")
    print(result["answer"])