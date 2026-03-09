
import requests
import random
import string
import sys

BASE_URL = "http://localhost:5000/api"

def random_str(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def run_test():
    print("Starting E2E test...")
    username = f"testUser_{random_str()}"
    email = f"{username}@test.com"
    password = "password123"

    print(f"1. Registering user: {username} ({email})...")
    res = requests.post(f"{BASE_URL}/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    if res.status_code != 201:
        print(f"FAILED: Registration failed with {res.status_code}: {res.text}")
        sys.exit(1)
    print("   Registration successful.")
    
    # Cookie should be set automatically in session if we used session, but requests doesn't persist unless we use a Session object.
    
    session = requests.Session()
    
    # Login to get cookie
    print("2. Logging in...")
    res = session.post(f"{BASE_URL}/login", json={
        "email": email,
        "password": password
    })
    if res.status_code != 200:
        print(f"FAILED: Login failed with {res.status_code}: {res.text}")
        sys.exit(1)
    print("   Login successful.")
    
    # Create post
    print("3. Creating 'Lost' post...")
    item_name = f"Lost Item {random_str()}"
    res = session.post(f"{BASE_URL}/posts", json={
        "post_type": "lost",
        "item_name": item_name,
        "location": "Test Location",
        "description": "This is a test description executed by debug script.",
        "place": "Test Place",
        "time": "Now"
    })
    if res.status_code != 201:
        print(f"FAILED: Create post failed with {res.status_code}: {res.text}")
        sys.exit(1)
    print(f"   Post created: {item_name}")

    # Verify post visibility
    print("4. Verifying post visibility...")
    res = session.get(f"{BASE_URL}/posts?type=lost")
    if res.status_code != 200:
        print(f"FAILED: Get posts failed with {res.status_code}: {res.text}")
        sys.exit(1)
    
    posts = res.json().get("data", {}).get("posts", [])
    found = False
    for p in posts:
        if p.get("item_name") == item_name:
            found = True
            break
    
    if found:
        print("SUCCESS! Post found in list.")
    else:
        print("FAILED: Post not found in list.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
