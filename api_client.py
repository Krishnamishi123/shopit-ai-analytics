
import os
import requests
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shopit.client")

API_URL = os.getenv(
    "API_BASE_URL",
    "https://shopit-ai-analytics.onrender.com"
).rstrip("/")

print("SHOPIT BACKEND URL:", API_URL)

def ask_shopit_api(question: str) -> dict:

    if not question or not question.strip():
        raise ValueError("Please enter a valid question.")

    try:
        response = requests.post(
            f"{API_URL}/chat/analytics",
            json={"question": question.strip()},
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            timeout=(10, 180)
        )

        response.raise_for_status()

        result = response.json()

        if not isinstance(result, dict):
            raise RuntimeError("Invalid response received from FastAPI.")

        records = result.get("data")

        if records is not None:
            result["data"] = pd.DataFrame(records)

        return result

    except requests.exceptions.ConnectTimeout as exc:
        raise RuntimeError(
            "Could not connect to the Shopit backend within 10 seconds."
        ) from exc

    except requests.exceptions.ReadTimeout as exc:
        raise RuntimeError(
            "Shopit backend took longer than 180 seconds. "
            "Check Render logs for the agent causing the delay."
        ) from exc

    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            f"Cannot connect to Shopit backend at {API_URL}: {exc}"
        ) from exc

    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(
            f"FastAPI returned HTTP {response.status_code}: "
            f"{response.text[:1000]}"
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            f"Shopit API request failed: {exc}"
        ) from exc