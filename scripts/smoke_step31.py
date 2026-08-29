"""Production-equivalent deployment smoke test."""
import os
import time

import httpx

base_url = os.getenv("SMOKE_BASE_URL", "http://127.0.0.1:8000")
api_key = os.environ["INFERENCE_API_KEY"]
headers = {"X-API-Key": api_key}

for _ in range(30):
    try:
        if httpx.get(f"{base_url}/health", timeout=2).status_code == 200:
            break
    except httpx.HTTPError:
        pass
    time.sleep(1)
else:
    raise SystemExit("health check failed")

assert httpx.get(f"{base_url}/ready", headers=headers, timeout=5).status_code == 200
metrics = httpx.get(f"{base_url}/metrics", timeout=5)
assert metrics.status_code == 200 and "inference_http_requests_total" in metrics.text
print("STEP 31 deployment smoke PASS")
