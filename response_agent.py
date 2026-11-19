
import json
import logging
import re

import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger("shopit")


# ==================================================
# 1. GEMINI CONFIGURATION
# ==================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash"
)


# ==================================================
# 2. DEFAULT RESPONSE
# ==================================================

def _default_response(
    answer: str,
    insights: list | None = None
) -> dict:

    return {
        "answer": answer,
        "insights": insights or [],
        "visualization_required": False,
        "chart_type": None,
        "x_column": None,
        "y_column": None,
        "chart_title": None
    }


# ==================================================
# 3. EXTRACT TEXT FROM GEMINI RESPONSE
# ==================================================

def _extract_text(content) -> str:

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, dict):
        return str(content.get("text", "")).strip()

    if isinstance(content, list):

        parts = []

        for block in content:

            if isinstance(block, str):
                parts.append(block)

            elif isinstance(block, dict):
                parts.append(
                    str(block.get("text", ""))
                )

            elif hasattr(block, "text"):
                parts.append(str(block.text))

        return "\n".join(parts).strip()

    if hasattr(content, "text"):
        return str(content.text).strip()

    return str(content).strip()


# ==================================================
# 4. EXTRACT JSON FROM GEMINI OUTPUT
# ==================================================

def _parse_json_response(text: str) -> dict:

    if not text:
        raise ValueError("Gemini returned an empty response.")

    # Remove Markdown code fences if present
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text.strip(),
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text.strip()
    )

    # Find the beginning of the JSON object
    start = text.find("{")

    if start == -1:
        raise ValueError(
            f"No JSON object found in Gemini response: {text[:500]}"
        )

    # Decode the first valid JSON object
    decoder = json.JSONDecoder()

    result, _ = decoder.raw_decode(text[start:])

    if not isinstance(result, dict):
        raise ValueError("Gemini response is not a JSON object.")

    return result


# ==================================================
# 5. FALLBACK ANSWER FROM SQL DATA
# ==================================================

def _fallback_from_dataframe(df: pd.DataFrame) -> str:

    if df is None or df.empty:
        return "No matching data was found."

    # Handle single-value results such as COUNT(*)
    if len(df) == 1 and len(df.columns) == 1:

        column = str(df.columns[0])
        value = df.iloc[0, 0]

        return (
            f"The query result is {value} "
            f"for the column '{column}'."
        )

    # Handle normal table results
    preview = df.head(5).to_dict(orient="records")

    return (
        f"The query returned {len(df)} rows "
        f"and {len(df.columns)} columns. "
        f"Here are the first results: {preview}"
    )


# ==================================================
# 6. MAIN DATA ANALYSIS FUNCTION
# ==================================================

def analyze_data(
    question: str,
    df: pd.DataFrame | None
) -> dict:

    # Handle missing results
    if df is None:
        return _default_response(
            "The database query could not be completed. Please try again."
        )

    if df.empty:
        return _default_response(
            "No matching data was found for this question."
        )

    columns = list(df.columns)

    # Prepare SQL results for Gemini
    data_text = df.head(100).to_string(index=False)

    if len(data_text) > 12000:
        data_text = data_text[:12000]

    prompt = f"""
You are Shopit's business analytics assistant.

USER QUESTION:
{question}

SQL RESULT:
{data_text}

ACTUAL RESULT COLUMN NAMES:
{json.dumps(columns)}

INSTRUCTIONS:

1. Answer the user's question directly.
2. Use only facts and numbers from the SQL result.
3. Never invent information.
4. Provide up to 4 useful business insights.
5. Do not repeat every row unnecessarily.
6. Request a chart only when it adds value.
7. Use bar for rankings and comparisons.
8. Use line for time trends.
9. Use pie for small part-to-whole breakdowns.
10. Use scatter for meaningful numeric relationships.
11. Column names must exactly match the actual SQL result columns.
12. The y_column must be numeric.
13. If no chart is needed, set visualization_required to false
    and all chart fields to null.

Return ONLY valid JSON.
Do not add Markdown fences or explanations.

Use exactly this structure:

{{
    "answer": "Your direct answer",
    "insights": [],
    "visualization_required": false,
    "chart_type": null,
    "x_column": null,
    "y_column": null,
    "chart_title": null
}}
"""

    # ==================================================
    # 7. CALL GEMINI
    # ==================================================

    try:

        logger.info(
            "Starting Gemini analysis | question=%s",
            question[:200]
        )

        response = llm.invoke(prompt)

        text = _extract_text(response.content)

        logger.info(
            "Gemini response received | response_length=%s",
            len(text)
        )

        result = _parse_json_response(text)

    except Exception as error:

        logger.exception(
            "Gemini analysis failed | error_type=%s",
            type(error).__name__
        )

        # Log a portion of the model output if JSON parsing failed
        if "text" in locals():
            logger.error(
                "Gemini raw response: %s",
                text[:1000]
            )

        # Return a factual answer from SQL data
        return _default_response(
            _fallback_from_dataframe(df)
        )

    # ==================================================
    # 8. NORMALIZE ANSWER
    # ==================================================

    answer = result.get("answer")

    if not isinstance(answer, str) or not answer.strip():
        answer = _fallback_from_dataframe(df)

    insights = result.get("insights", [])

    if not isinstance(insights, list):
        insights = []

    insights = [
        item.strip()
        for item in insights
        if isinstance(item, str) and item.strip()
    ][:4]

    # ==================================================
    # 9. VALIDATE VISUALIZATION
    # ==================================================

    visualization_required = (
        result.get("visualization_required") is True
    )

    chart_type = result.get("chart_type")
    x_column = result.get("x_column")
    y_column = result.get("y_column")
    chart_title = result.get("chart_title")

    allowed_charts = {
        "bar",
        "line",
        "pie",
        "scatter"
    }

    valid_chart = (
        visualization_required
        and chart_type in allowed_charts
        and isinstance(x_column, str)
        and isinstance(y_column, str)
        and x_column in columns
        and y_column in columns
    )

    if valid_chart:

        valid_chart = pd.api.types.is_numeric_dtype(
            df[y_column]
        )

    if not valid_chart:

        visualization_required = False
        chart_type = None
        x_column = None
        y_column = None
        chart_title = None

    # ==================================================
    # 10. RETURN FINAL RESPONSE
    # ==================================================

    return {
        "answer": answer,
        "insights": insights,
        "visualization_required": visualization_required,
        "chart_type": chart_type,
        "x_column": x_column,
        "y_column": y_column,
        "chart_title": chart_title
    }
