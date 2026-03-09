import requests
import time

BASE_URL = "http://localhost:5000/api"

def test_registration():
    print("Testing Registration...")
    ts = int(time.time())
    payload = {
        "username": f"verify_{ts}",
        "email": f"verify_{ts}@campus.edu",
        "password": "password123"
    }
    try:
        r = requests.post(f"{BASE_URL}/register", json=payload)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        if r.status_code == 201:
            print("✅ SUCCESS")
        else:
            print("❌ FAILED")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_registration()
