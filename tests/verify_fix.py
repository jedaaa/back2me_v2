
import requests

BASE_URL = "http://localhost:5000/api"

def verify_cookie_path():
    print("Testing login and checking cookie path...")
    # These are dummy credentials, we just want to see the Set-Cookie header if the server handles it
    # Actually, it's better to use a real attempt if possible, but even a failed login that sets a cookie would show it.
    # However, our login route only sets it on success.
    # I'll try to register a temporary user or just check the code again.
    # A better way is to see the raw response from the server.
    
    try:
        # Use a random email to avoid conflicts if previously registered
        import time
        ts = int(time.time())
        email = f"verify_{ts}@example.com"
        payload = {
            "username": f"user_{ts}",
            "email": email,
            "password": "password123"
        }
        
        response = requests.post(f"{BASE_URL}/register", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if 'Set-Cookie' in response.headers:
            cookie_header = response.headers['Set-Cookie']
            print(f"Set-Cookie Header: {cookie_header}")
            if 'Path=/' in cookie_header:
                print("SUCCESS: Cookie path is set to '/'")
            else:
                print("FAILURE: Cookie path is NOT set to '/'")
        else:
            print("FAILURE: No Set-Cookie header found in response. Check if registration was successful.")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    verify_cookie_path()
