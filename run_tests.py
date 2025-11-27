import json
import requests
import time


TEST_FILE = "tests.json"
API_URL = "http://127.0.0.1:5000/api/ask"

def run_single_test(test):
    payload = {
        "text": test["input"],
        "mode": test.get("mode", "general"),
        "notes": ""
    }

    try:
        r = requests.post(API_URL, json=payload, timeout=10)
    except Exception as e:
        return False, f"Request failed: {e}"

    if r.status_code != 200:
        return False, f"HTTP {r.status_code}"

    data = r.json()
    answer = data.get("answer", "").lower()

    # pattern check
    for pattern in test["expect_contains"]:
        if pattern.lower() not in answer:
            return False, f"Missing pattern: '{pattern}'"

    return True, "OK"


def run_tests():
    with open(TEST_FILE, "r", encoding="utf-8") as f:
        tests = json.load(f)

    passed = 0

    print("\n=== Running Offline Evaluation ===\n")

    for i, test in enumerate(tests, 1):
        ok, msg = run_single_test(test)
        if ok:
            passed += 1
            print(f"Test {i}: PASS")
        else:
            print(f"Test {i}: FAIL — {msg}")

    print("\n==============================")
    print(f"Passed {passed}/{len(tests)} tests")
    print("==============================\n")


if __name__ == "__main__":
    run_tests()
