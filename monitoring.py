
import logging
import os
import time
import csv
import uuid
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from threading import Lock

from graph import shopit_graph


# ==================================================
# 1. PATH CONFIGURATION
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_PATH = os.path.join(LOG_DIR, "shopit.log")
METRICS_PATH = os.path.join(LOG_DIR, "metrics.csv")

os.makedirs(LOG_DIR, exist_ok=True)

CSV_LOCK = Lock()


# ==================================================
# 2. LOGGING CONFIGURATION
# ==================================================

logger = logging.getLogger("shopit")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:

    handler = RotatingFileHandler(
        LOG_PATH,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)


# ==================================================
# 3. CSV METRICS CONFIGURATION
# ==================================================

CSV_FIELDS = [
    "request_id",
    "timestamp",
    "category",
    "status",
    "duration_seconds",
    "error_type",
]


def initialize_metrics_file():

    if not os.path.exists(METRICS_PATH):

        with CSV_LOCK:

            if not os.path.exists(METRICS_PATH):

                with open(
                    METRICS_PATH,
                    "w",
                    newline="",
                    encoding="utf-8",
                ) as file:

                    writer = csv.DictWriter(
                        file,
                        fieldnames=CSV_FIELDS,
                    )

                    writer.writeheader()


initialize_metrics_file()


# ==================================================
# 4. SAVE METRICS
# ==================================================

def save_metrics(
    request_id,
    category,
    status,
    duration,
    error_type=None,
):

    record = {
        "request_id": request_id,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "category": category,
        "status": status,
        "duration_seconds": round(duration, 4),
        "error_type": error_type or "",
    }

    with CSV_LOCK:

        with open(
            METRICS_PATH,
            "a",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=CSV_FIELDS,
            )

            writer.writerow(record)


# ==================================================
# 5. MAIN SHOPIT QUERY MONITORING
# ==================================================

def run_shopit_query(question: str) -> dict:
    """
    Execute Shopit LangGraph workflow
    and record operational metrics.
    """

    start_time = time.perf_counter()

    request_id = str(uuid.uuid4())

    category = "UNKNOWN"
    status = "SUCCESS"
    error_type = None  #render,mini projects,project intro 5 min,how to monitor the system,objective,goal,tech stack,evalauate,challenges

    logger.info(
        "Request started | request_id=%s | question_length=%s",
        request_id,
        len(question),
    )

    initial_state = {
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
        "chart_title": None,
    }

    try:

        result = shopit_graph.invoke(initial_state)

        category = result.get("category", "UNKNOWN")

        answer = result.get("answer", "")

        logger.info(
            "Request completed | request_id=%s | "
            "category=%s | answer_present=%s",
            request_id,
            category,
            bool(answer),
        )

        return result

    except Exception as error:

        status = "FAILURE"
        error_type = type(error).__name__

        logger.exception(
            "Request failed | request_id=%s",
            request_id,
        )

        raise

    finally:

        elapsed_seconds = (
            time.perf_counter() - start_time
        )

        save_metrics(
            request_id=request_id,
            category=category,
            status=status,
            duration=elapsed_seconds,
            error_type=error_type,
        )

        logger.info(
            "Request metrics saved | request_id=%s | "
            "duration_seconds=%.2f | status=%s",
            request_id,
            elapsed_seconds,
            status,
        )


# ==================================================
# 6. MONITORING SUMMARY
# ==================================================

def get_monitoring_summary():

    initialize_metrics_file()

    total_requests = 0
    successful_requests = 0
    failed_requests = 0

    total_duration = 0
    categories = {}

    with CSV_LOCK:

        with open(
            METRICS_PATH,
            "r",
            newline="",
            encoding="utf-8",
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                total_requests += 1

                if row["status"] == "SUCCESS":
                    successful_requests += 1

                else:
                    failed_requests += 1

                total_duration += float(
                    row["duration_seconds"]
                )

                category = row["category"]

                categories[category] = (
                    categories.get(category, 0) + 1
                )

    average_response_time = (
        total_duration / total_requests
        if total_requests else 0
    )

    success_rate = (
        successful_requests / total_requests * 100
        if total_requests else 0
    )

    return {
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "success_rate_percent": round(
            success_rate, 2
        ),
        "average_response_time_seconds": round(
            average_response_time, 4
        ),
        "requests_by_category": categories,
    }
