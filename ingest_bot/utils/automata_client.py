"""Simple Automata API client for integration tests.

Usage:
    # Run a quick end-to-end test (login -> start -> status -> stop)
    python -m ingest_bot.utils.automata_client

Environment variables supported:
    AUTOMATA_URL (default: http://127.0.0.1:5000)
    AUTOMATA_USER (default: admin)
    AUTOMATA_PASS (default: admin123)
"""

import os
import sys
import requests

AUTOMATA_URL = os.getenv("AUTOMATA_URL", "http://127.0.0.1:5000")
USER = os.getenv("AUTOMATA_USER", "admin")
PASS = os.getenv("AUTOMATA_PASS", "admin123")


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def login(username: str = USER, password: str = PASS) -> str:
    url = f"{AUTOMATA_URL}/api/auth/login"
    r = requests.post(url, json={"username": username, "password": password}, timeout=10)
    r.raise_for_status()
    data = r.json()
    return data.get("access_token")


def start_system(token: str) -> dict:
    url = f"{AUTOMATA_URL}/api/status/start"
    r = requests.post(url, headers=_auth_header(token), timeout=10)
    r.raise_for_status()
    return r.json()


def stop_system(token: str) -> dict:
    url = f"{AUTOMATA_URL}/api/status/stop"
    r = requests.post(url, headers=_auth_header(token), timeout=10)
    r.raise_for_status()
    return r.json()


def get_status(token: str) -> dict:
    url = f"{AUTOMATA_URL}/api/status"
    r = requests.get(url, headers=_auth_header(token), timeout=10)
    r.raise_for_status()
    return r.json()


def run_integration_test():
    print(f"Automata URL: {AUTOMATA_URL}")
    token = login()
    print("Logged in, token length:", len(token))

    print("Calling /api/status/start...")
    resp = start_system(token)
    print("start response:", resp)

    print("Fetching /api/status...")
    status = get_status(token)
    print("status:", status)

    print("Calling /api/status/stop...")
    resp = stop_system(token)
    print("stop response:", resp)


if __name__ == '__main__':
    try:
        run_integration_test()
    except Exception as e:
        print("Integration test failed:", e, file=sys.stderr)
        sys.exit(1)
    else:
        print("Integration test succeeded")
