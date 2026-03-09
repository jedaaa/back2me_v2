import requests

BASE_URL = "http://localhost:5000"

print("1. Testing GET /api/register (Should be 405 as it only allows POST)")
r = requests.get(f"{BASE_URL}/api/register")
print(f"GET /api/register: {r.status_code} {r.reason}")

print("\n2. Testing POST /api/register (Should be 201 or similar error like 400/409)")
r = requests.post(f"{BASE_URL}/api/register", json={
    "username": "testuser",
    "email": "test@test.com",
    "password": "password123"
})
print(f"POST /api/register: {r.status_code} {r.reason}")
print(f"Body: {r.text}")

print("\n3. Testing POST /pages/register.html (Checking if serve_spa allows POST)")
r = requests.post(f"{BASE_URL}/pages/register.html")
print(f"POST /pages/register.html: {r.status_code} {r.reason}")
