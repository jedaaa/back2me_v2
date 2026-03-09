
import requests

BASE_URL = "http://localhost:5000"

def test_endpoints():
    print(f"Testing endpoints on {BASE_URL}")
    
    # 1. Test POST to /api/login (Should be allowed)
    try:
        r = requests.post(f"{BASE_URL}/api/login", json={"email": "test@example.com", "password": "password"})
        print(f"POST /api/login: {r.status_code} {r.reason}")
    except Exception as e:
        print(f"POST /api/login Error: {e}")

    # 2. Test POST to /pages/login.html (Should be 405 if serve_spa doesn't allow POST)
    try:
        r = requests.post(f"{BASE_URL}/pages/login.html", data={"email": "test@example.com"})
        print(f"POST /pages/login.html: {r.status_code} {r.reason}")
    except Exception as e:
        print(f"POST /pages/login.html Error: {e}")

    # 3. Test GET to /api/me
    try:
        r = requests.get(f"{BASE_URL}/api/me")
        print(f"GET /api/me: {r.status_code} {r.reason}")
    except Exception as e:
        print(f"GET /api/me Error: {e}")

if __name__ == "__main__":
    test_endpoints()
