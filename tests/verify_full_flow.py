
import requests
import time

BASE_URL = "http://localhost:5000/api"

def test_full_flow():
    session = requests.Session()
    username = f"user_{int(time.time())}"
    email = f"{username}@test.com"
    password = "password123"

    print(f"Step 1: Registering {email}...")
    r_reg = session.post(f"{BASE_URL}/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    print(f"Register Status: {r_reg.status_code}")
    print(f"Cookies after register: {session.cookies.get_dict()}")

    print("\nStep 2: Checking session (me)...")
    r_me1 = session.get(f"{BASE_URL}/me")
    print(f"Me Status: {r_me1.status_code}")
    print(f"Cookies after me: {session.cookies.get_dict()}")

    print("\nStep 3: Logging out...")
    r_logout = session.post(f"{BASE_URL}/logout")
    print(f"Logout Status: {r_logout.status_code}")
    print(f"Set-Cookie in logout response: {r_logout.headers.get('Set-Cookie')}")
    print(f"Cookies after logout: {session.cookies.get_dict()}")

    print("\nStep 4: Checking session after logout...")
    r_me2 = session.get(f"{BASE_URL}/me")
    print(f"Me Status (expected 401): {r_me2.status_code}")
    if r_me2.status_code == 200:
        print("ALERT: Logout did not clear the session in the session object!")
    
    print("\nStep 5: Logging in...")
    r_login = session.post(f"{BASE_URL}/login", json={
        "email": email,
        "password": password
    })
    print(f"Login Status: {r_login.status_code}")
    print(f"Cookies after login: {session.cookies.get_dict()}")
    
    print("\nStep 6: Checking session after login...")
    r_me3 = session.get(f"{BASE_URL}/me")
    print(f"Me Status (expected 200): {r_me3.status_code}")
    print(f"Cookies after final me: {session.cookies.get_dict()}")

if __name__ == "__main__":
    test_full_flow()
