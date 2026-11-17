import os
import re
import pandas as pd

from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy import text

from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY missing in .env"
    )



DATABASE_URL = "sqlite:///shopit.db"

engine = create_engine(
    DATABASE_URL
)



llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0
)



def get_schema():

    schema = ""

    with engine.connect() as conn:

        tables = conn.execute(
            text(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                """
            )
        )

        tables = [row[0] for row in tables]

        for table in tables:

            schema += f"\nTABLE: {table}\n"

            columns = conn.execute(
                text(
                    f"PRAGMA table_info({table})"
                )
            )

            for column in columns:

                schema += (
                    f"{column[1]} ({column[2]})\n"
                )

    return schema

def generate_sql(question):

    schema = get_schema()

    prompt = f"""
You are an expert SQLite analyst.

Convert the user's question into SQL.

Return ONLY SQL.

Database Schema:

{schema}

Question:

{question}
"""

    response = llm.invoke(prompt)

    print("\nCONTENT TYPE:")
    print(type(response.content))

    print("\nRAW CONTENT:")
    print(response.content)

    # ----------------------------------
    # Extract SQL from Gemini response
    # ----------------------------------

    if isinstance(response.content, str):

        sql = response.content

    elif isinstance(response.content, list):

        sql_parts = []

        for item in response.content:

            if isinstance(item, dict):

                sql_parts.append(
                    item.get("text", "")
                )

            else:

                sql_parts.append(
                    str(item)
                )

        sql = "".join(sql_parts)

    else:

        sql = str(response.content)

    # ----------------------------------
    # Clean markdown
    # ----------------------------------

    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")
    sql = sql.strip()

    print("\nEXTRACTED SQL:")
    print(sql)

    return sql

# =====================================================
# SQL VALIDATION
# =====================================================

def validate_sql(sql):

    sql_lower = sql.lower()

    dangerous_keywords = [

        "drop",
        "delete",
        "update",
        "insert",
        "alter",
        "truncate",
        "replace",
        "create"
    ]

    for keyword in dangerous_keywords:

        if re.search(
            rf"\b{keyword}\b",
            sql_lower
        ):
            raise Exception(
                f"Unsafe SQL Detected : {keyword}"
            )

    return True


# =====================================================
# EXECUTE SQL
# =====================================================

def execute_sql(sql):

    with engine.connect() as conn:

        result = pd.read_sql(
            sql,
            conn
        )

    return result



def analyze_results(
    question,
    dataframe
):

    prompt = f"""
You are a business analyst.

User Question:

{question}

Query Results:

{dataframe.to_string(index=False)}

Provide:

1. Direct answer
2. Key insights
3. Business interpretation

Keep answer concise.
"""

    response = llm.invoke(prompt)

    if isinstance(response.content, list):
        answer = "".join(
            block.get("text", "")
            for block in response.content
            if isinstance(block, dict)
            and block.get("type") == "text"
        )
    else:
        answer = response.content

    return answer


def ask_database(question):

    print("\nGenerating SQL...\n")

    sql = generate_sql(question)

    print("=" * 60)
    print("GENERATED SQL")
    print("=" * 60)
    print(sql)

    validate_sql(sql)

    print("\nExecuting SQL...\n")

    results = execute_sql(sql)

    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(results.head())

    answer = analyze_results(
        question,
        results
    )

    return answer


if __name__ == "__main__":

    while True:

        question = input(
            "\nAsk a business question (q to exit): "
        )

        if question.lower() == "q":
            break

        try:

            answer = ask_database(
                question
            )

            print("\n")
            print("=" * 60)
            print("FINAL ANSWER")
            print("=" * 60)
            print(answer)

        except Exception as e:

            print(
                "\nERROR:",
                str(e)
            )