"""Call GET /api/demo once while the API is running to pre-warm Claude before a demo."""

from __future__ import annotations

import os
import sys
import time
import urllib.error
import urllib.request


def main() -> None:
    base = os.environ.get("STAYRIGHT_API_URL", "http://127.0.0.1:5000").rstrip("/")
    url = f"{base}/api/demo"

    print("Warming up model...", flush=True)
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=180) as resp:
            resp.read()
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        elapsed_ms = (time.perf_counter() - t0) * 1000
        print(f"Response time: {elapsed_ms:.0f} ms", flush=True)
        print(str(e), file=sys.stderr, flush=True)
        sys.exit(1)

    elapsed_ms = (time.perf_counter() - t0) * 1000
    print(f"Response time: {elapsed_ms:.0f} ms", flush=True)

    if elapsed_ms < 4000:
        print("Ready. First query will be fast.", flush=True)
    else:
        print("Warning: slow response. Check API key and connection.", flush=True)


if __name__ == "__main__":
    main()
