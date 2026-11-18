
import os
import requests
import pandas as pd

# Read the FastAPI URL from environment variables.
# Localhost is used automatically when running locally.
API_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


def ask_shopit_api(question: str) -> dict:
    try:
        response = requests.post(
            f"{API_URL}/chat/analytics",
            json={"question": question},
            timeout=180,
        )

    except requests.RequestException as exc:
        raise RuntimeError(
            f"Cannot reach FastAPI at {API_URL}: {exc}"
        ) from exc

    if not response.ok:
        print("FastAPI status:", response.status_code)
        print("FastAPI response:", response.text)

        raise RuntimeError(
            f"FastAPI returned HTTP {response.status_code}: "
            f"{response.text}"
        )

    result = response.json()

    records = result.get("data")

    if records is not None:
        result["data"] = pd.DataFrame(records)

    return result
