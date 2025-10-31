import sys, requests
URL = "http://localhost:8080/health"
try:
    r = requests.get(URL, timeout=3)
    ok = (r.status_code == 200 and r.json().get("status") == "up")
    sys.exit(0 if ok else 2)
except Exception:
    sys.exit(2)
