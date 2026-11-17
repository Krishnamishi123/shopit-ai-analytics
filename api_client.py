
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"


def ask_shopit_api(question: str) -> dict:
    try:
        response = requests.post(
            f"{API_URL}/chat/analytics",
            json={"question": question},
            timeout=180,
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Cannot reach FastAPI: {exc}"
        ) from exc

    # Show the actual error returned by FastAPI.
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
