
import os
import requests
import pandas as pd

# Use Render backend by default.
# You can override this using API_BASE_URL.
API_URL = os.getenv(
    "API_BASE_URL",
    "https://shopit-ai-analytics.onrender.com"
).rstrip("/")

print("SHOPIT BACKEND URL:", API_URL)


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
        raise RuntimeError(
            f"FastAPI returned HTTP {response.status_code}: "
            f"{response.text}"
        )

    result = response.json()

    records = result.get("data")

    if records is not None:
        result["data"] = pd.DataFrame(records)

    return result
