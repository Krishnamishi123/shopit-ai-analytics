
import json
import logging

import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger("shopit")

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash"
)


def _default_response(
    answer: str,
    insights: list | None = None
) -> dict:
    """Return every field expected by graph.py and Streamlit."""

    return {
        "answer": answer,
        "insights": insights or [],
        "visualization_required": False,
        "chart_type": None,
        "x_column": None,
        "y_column": None,
        "chart_title": None
    }


def _extract_text(content) -> str:
    """Handle Gemini responses returned as text or content blocks."""

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []

        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))

        return "".join(parts).strip()

    return str(content).strip()


def analyze_data(question: str, df: pd.DataFrame | None) -> dict:
    """Turn SQL results into a business answer and optional chart instructions."""

    # Step 1: Handle missing or empty query results
    if df is None:
        return _default_response(
            "The database query could not be completed. Please try again."
        )

    if df.empty:
        return _default_response(
            "No matching data was found for this question."
        )

    # Step 2: Prepare the result for Gemini
    data_text = df.head(100).to_string(index=False)

    if len(data_text) > 12000:
        data_text = data_text[:12000]

    columns = list(df.columns)

    prompt = f"""
You are Shopit's business analytics assistant.

USER QUESTION:
{question}

SQL RESULT:
{data_text}

ACTUAL RESULT COLUMN NAMES:
{json.dumps(columns)}

Rules:
- Answer the question directly.
- Use only facts and numbers present in the SQL result.
- Never invent numbers or claim unsupported facts.
- Give up to 4 concise insights when meaningful.
- Do not repeat every row unnecessarily.
- Request a chart only if it would help explain multiple rows.
- Use "bar" for rankings and category/product/customer comparisons.
- Use "line" for time trends, "pie" for a small part-to-whole breakdown,
  and "scatter" for two meaningful numeric variables.
- x_column and y_column must exactly match actual column names.
- Use a numeric y_column for bar, line, and scatter charts.
- Do not invent or rename columns.
- If no suitable chart is needed, set visualization_required to false
  and set chart_type, x_column, y_column, chart_title to null.
- Return valid JSON only, with no Markdown fences.

Return exactly these keys:
{{
  "answer": "string",
  "insights": ["string"],
  "visualization_required": false,
  "chart_type": null,
  "x_column": null,
  "y_column": null,
  "chart_title": null
}}
"""

    # Step 3: Ask Gemini to analyze the data
    try:
        response = llm.invoke(prompt)
        text = _extract_text(response.content)

        # Remove optional Markdown fences
        if text.startswith("```"):
            lines = text.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            text = "\n".join(lines).strip()

        result = json.loads(text)

        if not isinstance(result, dict):
            raise ValueError("Gemini response was not a JSON object.")

    except Exception:
        logger.exception("Response analysis failed; using fallback response")

        # Basic fallback based on actual database output
        return _default_response(
            f"The query returned {len(df)} rows and "
            f"{len(columns)} columns. I couldn't generate a full "
            "business summary right now. Please try again."
        )

    # Step 4: Normalize the response fields
    answer = result.get("answer")

    if not isinstance(answer, str) or not answer.strip():
        answer = f"The query returned {len(df)} rows."

    insights = result.get("insights", [])

    if not isinstance(insights, list):
        insights = []

    insights = [
        item for item in insights
        if isinstance(item, str) and item.strip()
    ][:4]

    visualization_required = (
        result.get("visualization_required") is True
    )

    chart_type = result.get("chart_type")
    x_column = result.get("x_column")
    y_column = result.get("y_column")
    chart_title = result.get("chart_title")

    # Step 5: Validate chart instructions against the real DataFrame
    allowed_charts = {"bar", "line", "pie", "scatter"}

    valid_chart = (
        visualization_required
        and chart_type in allowed_charts
        and isinstance(x_column, str)
        and isinstance(y_column, str)
        and x_column in columns
        and y_column in columns
    )

    if valid_chart:
        # Charts should use numeric values for their y-axis.
        valid_chart = pd.api.types.is_numeric_dtype(df[y_column])

    if not valid_chart:
        visualization_required = False
        chart_type = None
        x_column = None
        y_column = None
        chart_title = None

    return {
        "answer": answer,
        "insights": insights,
        "visualization_required": visualization_required,
        "chart_type": chart_type,
        "x_column": x_column,
        "y_column": y_column,
        "chart_title": chart_title
    }
