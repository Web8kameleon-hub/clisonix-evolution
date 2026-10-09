import requests  # type: ignore[import-untyped]
from requests.adapters import HTTPAdapter  # type: ignore[import-untyped]
from urllib3.util.retry import Retry


def _check_stream_api(session: requests.Session, url: str, timeout: int = 15) -> tuple[str, int]:
    payload = {
        "topic": "health check",
        "personas": ["alba"],
        "max_tokens": -1,  # unlimited
        "stream_mode": "json",
    }
    headers = {
        "Accept": "text/event-stream",
        "Content-Type": "application/json",
    }

    with session.post(url, json=payload, headers=headers, stream=True, timeout=timeout) as response:
        if response.status_code != 200:
            return f"⚠️ CODE: {response.status_code}", len(response.content)

        content_type = response.headers.get("Content-Type", "")
        if "text/event-stream" not in content_type.lower():
            return f"⚠️ CODE: 200 (unexpected content-type: {content_type})", 0

        first_event = None
        bytes_seen = 0
        for line in response.iter_lines(decode_unicode=True):
            if line is None:
                continue
            bytes_seen += len(line.encode("utf-8"))
            if line.strip():
                first_event = line.strip()
                break

        if first_event:
            return "✅ ONLINE", bytes_seen

        return "⚠️ CODE: 200 (empty stream)", bytes_seen


def check_clisonix_health() -> None:
    endpoints = {
        "Web Debate": {
            "url": "https://clisonix.com/debate",
            "method": "GET",
        },
        "Stream API": {
            "url": "https://api.clisonix.com/api/v1/debate/stream",
            "method": "POST_STREAM",
        },
        "Status API": {
            "url": "https://api.clisonix.com/api/v1/status",
            "method": "GET",
        },
    }

    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

    print("--- CLISONIX ADVANCED MONITORING (Admin: Ledjan) ---")

    for name, endpoint in endpoints.items():
        try:
            method = endpoint["method"]
            url = endpoint["url"]

            if method == "POST_STREAM":
                status, size = _check_stream_api(session, url)
                print(f"{name:12} -> {status} ({size} bytes)")
                continue

            response = session.get(url, timeout=10)
            status = "✅ ONLINE" if response.status_code == 200 else f"⚠️ CODE: {response.status_code}"
            print(f"{name:12} -> {status} ({len(response.content)} bytes)")
        except requests.exceptions.RequestException as error:
            print(f"{name:12} -> ❌ ERROR: {str(error)}")


if __name__ == "__main__":
    check_clisonix_health()