
# api.py
import time
import json
import logging
import math
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from monitoring import get_monitoring_summary
from monitoring import run_shopit_query
import logging
import sys
import traceback
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True
)

logger = logging.getLogger("shopit")
# --------------------------------------------------
# PATHS AND LOGGING
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
logger = logging.getLogger("shopit")

# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="Shopit AI Analytics API",
    description=(
        "Ask questions about Shopit business data and "
        "Shopit company policies using the existing AI assistant."
    ),
    version="1.0.0",
)


# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Question to ask the Shopit AI assistant",
    )


# --------------------------------------------------
# RESPONSE MODEL
# --------------------------------------------------

class ChatResponse(BaseModel):
    question: str
    category: Optional[str] = None
    answer: str
    sql: Optional[str] = None
    insights: list[Any] = Field(default_factory=list)
    visualization_required: bool = False
    chart_type: Optional[str] = None
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    chart_title: Optional[str] = None
    data: Optional[list[dict[str, Any]]] = None


# --------------------------------------------------
# HELPER: CONVERT GRAPH DATA INTO JSON-SAFE DATA
# --------------------------------------------------
@app.get("/monitoring/summary")
def monitoring_summary():

    return get_monitoring_summary()
def dataframe_to_records(data) -> Optional[list[dict[str, Any]]]:
    """
    Convert a pandas DataFrame into JSON-compatible records.
    Return None when no DataFrame is available.
    """
    if data is None:
        return None

    if not hasattr(data, "to_json"):
        logger.warning(
            "Graph returned data that is not a pandas DataFrame: %s",
            type(data).__name__,
        )
        return None

    try:
        # pandas converts NaN and NaT to JSON null.
        json_text = data.to_json(
            orient="records",
            date_format="iso",
        )
        return json.loads(json_text)
    except Exception:
        logger.exception("Could not serialize DataFrame")
        return None


def safe_string(value, default=""):
    if value is None:
        return default

    if isinstance(value, str):
        return value

    return str(value)


def normalize_insights(value) -> list[Any]:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    return [value]


# --------------------------------------------------
# ENDPOINT 1: ROOT
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Welcome to the Shopit AI Analytics API",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


# --------------------------------------------------
# ENDPOINT 2: HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():
    database_path = BASE_DIR / "shopit.db"
    vectorstore_path = BASE_DIR / "vectorstore"

    return {
        "status": "ok",
        "api": "running",
        "database_file_exists": database_path.is_file(),
        "vectorstore_directory_exists": vectorstore_path.is_dir(),
    }


# --------------------------------------------------
# SHARED CHAT PROCESSOR
# --------------------------------------------------


def process_chat(question: str) -> ChatResponse:

    question = question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty."
        )

    start_time = time.perf_counter()

    logger.info(
        "SHOPIT REQUEST STARTED | question=%s",
        question[:200]
    )

    try:

        logger.info("Starting LangGraph execution")

        result = run_shopit_query(question)

        graph_time = time.perf_counter() - start_time

        logger.info(
            "LangGraph completed in %.2f seconds",
            graph_time
        )

        if not isinstance(result, dict):
            raise ValueError(
                "Unexpected graph result type: "
                f"{type(result).__name__}"
            )

        api_start = time.perf_counter()

        response = ChatResponse(
            question=question,
            category=result.get("category"),
            answer=safe_string(
                result.get("answer"),
                "The assistant did not return an answer."
            ),
            sql=result.get("sql"),
            insights=normalize_insights(
                result.get("insights")
            ),
            visualization_required=bool(
                result.get("visualization_required", False)
            ),
            chart_type=result.get("chart_type"),
            x_column=result.get("x_column"),
            y_column=result.get("y_column"),
            chart_title=result.get("chart_title"),
            data=dataframe_to_records(result.get("data"))
        )

        total_time = time.perf_counter() - start_time

        logger.info(
            "SHOPIT REQUEST COMPLETED | "
            "graph_time=%.2fs | total_time=%.2fs",
            graph_time,
            total_time
        )

        return response

    except HTTPException:
        raise

    except Exception:

        logger.exception("SHOPIT REQUEST FAILED")

        raise HTTPException(
            status_code=500,
            detail="Shopit could not process your question."
        )

# --------------------------------------------------
# ENDPOINT 3: CHAT
# --------------------------------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    General-purpose endpoint for Shopit questions.
    """
    return process_chat(request.question)


# --------------------------------------------------
# ENDPOINT 4: ANALYTICS
# --------------------------------------------------

@app.post("/chat/analytics", response_model=ChatResponse)
def chat_analytics(request: ChatRequest):

    return process_chat(request.question)