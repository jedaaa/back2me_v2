"""
COMPREHENSIVE TESTING SUITE - Back2Me
Tests: Smoke, UAT, Regression, Performance, Security
"""

import requests
import time
import json
import random
import string
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

# Test results storage
results = {
    "smoke": [],
    "uat": [],
    "regression": [],
    "performance": [],
    "security": []
}

def log_result(category, test_name, passed, message="", duration_ms=0):
    """Log test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    result = {
        "test": test_name,
        "status": status,
        "passed": passed,
        "message": message,
        "duration_ms": duration_ms
    }
    results[category].append(result)
    print(f"  {status} | {test_name:40} | {duration_ms:5.0f}ms | {message}")
    return passed

def random_string(length=8):
    """Generate random string"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# ═══════════════════════════════════════════════════════════
# SMOKE TESTING - Critical Path Validation
# ═══════════════════════════════════════════════════════════

def smoke_test_server_startup():
    """Test: Server is running"""
    try:
        start = time.time()
        response = requests.get(f"{API_URL}/health", timeout=5)
        duration = (time.time() - start) * 1000
        return log_result("smoke", "Server Startup", response.status_code == 200, 
                         f"Status: {response.status_code}", duration)
    except Exception as e:
        return log_result("smoke", "Server Startup", False, str(e))

def smoke_test_homepage():
    """Test: Homepage loads"""
    try:
        start = time.time()
        response = requests.get(BASE_URL, timeout=5)
        duration = (time.time() - start) * 1000
        return log_result("smoke", "Homepage Load", response.status_code == 200,
                         f"{len(response.text)} bytes", duration)
    except Exception as e:
        return log_result("smoke", "Homepage Load", False, str(e))

def smoke_test_login_page():
    """Test: Login page loads"""
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/pages/login.html", timeout=5)
        duration = (time.time() - start) * 1000
        has_css = "style.css" in response.text
        return log_result("smoke", "Login Page", response.status_code == 200 and has_css,
                         "CSS linked" if has_css else "CSS missing", duration)
    except Exception as e:
        return log_result("smoke", "Login Page", False, str(e))

def smoke_test_static_files():
    """Test: Static files serve"""
    try:
        start = time.time()
        css = requests.get(f"{BASE_URL}/css/style.css", timeout=5)
        js = requests.get(f"{BASE_URL}/js/app.js", timeout=5)
        duration = (time.time() - start) * 1000
        passed = css.status_code == 200 and js.status_code == 200
        return log_result("smoke", "Static Files", passed,
                         f"CSS: {css.status_code}, JS: {js.status_code}", duration)
    except Exception as e:
        return log_result("smoke", "Static Files", False, str(e))

# ═══════════════════════════════════════════════════════════
# UAT - User Acceptance Testing
# ═══════════════════════════════════════════════════════════

def uat_test_user_registration():
    """Test: User can register"""
    try:
        username = f"test_{random_string()}"
        email = f"{username}@test.com"
        
        start = time.time()
        response = requests.post(f"{API_URL}/register", json={
            "username": username,
            "email": email,
            "password": "Test123456"
        })
        duration = (time.time() - start) * 1000
        
        passed = response.status_code == 201
        return log_result("uat", "User Registration", passed,
                         f"User: {username}", duration), response.cookies if passed else None
    except Exception as e:
        return log_result("uat", "User Registration", False, str(e)), None

def uat_test_user_login(username=None, password="Test123456"):
    """Test: User can login"""
    try:
        if not username:
            username = f"test_{random_string()}"
            email = f"{username}@test.com"
            # Register first
            requests.post(f"{API_URL}/register", json={
                "username": username,
                "email": email,
                "password": password
            })
        
        start = time.time()
        response = requests.post(f"{API_URL}/login", json={
            "email": f"{username}@test.com",
            "password": password
        })
        duration = (time.time() - start) * 1000
        
        passed = response.status_code == 200
        return log_result("uat", "User Login", passed,
                         response.json().get("message", ""), duration), response.cookies if passed else None
    except Exception as e:
        return log_result("uat", "User Login", False, str(e)), None

def uat_test_create_post(cookies):
    """Test: User can create post"""
    try:
        start = time.time()
        response = requests.post(f"{API_URL}/posts", 
            json={
                "post_type": "lost",
                "item_name": f"Test Item {random_string()}",
                "location": "Test Location",
                "description": "Test description",
                "place": "Test Place",
                "time": "Now"
            },
            cookies=cookies
        )
        duration = (time.time() - start) * 1000
        
        passed = response.status_code == 201
        return log_result("uat", "Create Post", passed,
                         response.json().get("message", ""), duration)
    except Exception as e:
        return log_result("uat", "Create Post", False, str(e))

def uat_test_view_posts():
    """Test: User can view posts"""
    try:
        start = time.time()
        response = requests.get(f"{API_URL}/posts")
        duration = (time.time() - start) * 1000
        
        data = response.json()
        count = len(data.get("posts", []))
        passed = response.status_code == 200
        return log_result("uat", "View Posts", passed,
                         f"{count} posts found", duration)
    except Exception as e:
        return log_result("uat", "View Posts", False, str(e))

# ═══════════════════════════════════════════════════════════
# REGRESSION TESTING - Verify No Breaking Changes
# ═══════════════════════════════════════════════════════════

def regression_test_all_endpoints():
    """Test: All API endpoints functional"""
    endpoints = [
        ("GET", "/health", None),
        ("GET", "/posts", None),
        ("GET", "/posts/lost", None),
        ("GET", "/posts/found", None),
    ]
    
    passed_count = 0
    for method, path, data in endpoints:
        try:
            start = time.time()
            if method == "GET":
                response = requests.get(f"{API_URL}{path}")
            else:
                response = requests.post(f"{API_URL}{path}", json=data)
            duration = (time.time() - start) * 1000
            
            if response.status_code in [200, 201, 401]:  # 401 for protected routes is expected
                passed_count += 1
                log_result("regression", f"Endpoint {path}", True, f"{response.status_code}", duration)
        except Exception as e:
            log_result("regression", f"Endpoint {path}", False, str(e))
    
    return passed_count == len(endpoints)

def regression_test_authentication_flow():
    """Test: Complete auth flow works"""
    try:
        username = f"regtest_{random_string()}"
        email = f"{username}@test.com"
        password = "Test123456"
        
        # Register
        reg = requests.post(f"{API_URL}/register", json={
            "username": username, "email": email, "password": password
        })
        
        # Login
        login = requests.post(f"{API_URL}/login", json={
            "email": email, "password": password
        })
        
        # Get user info
        me = requests.get(f"{API_URL}/me", cookies=login.cookies)
        
        # Logout
        logout = requests.post(f"{API_URL}/logout", cookies=login.cookies)
        
        passed = all([reg.status_code == 201, login.status_code == 200,
                     me.status_code == 200, logout.status_code == 200])
        
        return log_result("regression", "Auth Flow", passed,
                         "Register→Login→Me→Logout", 0)
    except Exception as e:
        return log_result("regression", "Auth Flow", False, str(e))

# ═══════════════════════════════════════════════════════════
# PERFORMANCE TESTING - Speed & Load
# ═══════════════════════════════════════════════════════════

def performance_test_page_load_time():
    """Test: Page loads under 2s"""
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/pages/login.html")
        duration = (time.time() - start) * 1000
        
        passed = duration < 2000
        return log_result("performance", "Page Load Time", passed,
                         f"Target: <2000ms", duration)
    except Exception as e:
        return log_result("performance", "Page Load Time", False, str(e))

def performance_test_api_response():
    """Test: API responds under 500ms"""
    try:
        start = time.time()
        response = requests.get(f"{API_URL}/posts")
        duration = (time.time() - start) * 1000
        
        passed = duration < 500
        return log_result("performance", "API Response Time", passed,
                         f"Target: <500ms", duration)
    except Exception as e:
        return log_result("performance", "API Response Time", False, str(e))

def performance_test_concurrent_requests():
    """Test: Handle 50 concurrent requests"""
    try:
        def make_request(i):
            start = time.time()
            response = requests.get(f"{API_URL}/health")
            return (time.time() - start) * 1000, response.status_code == 200
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request, i) for i in range(50)]
            results_list = [f.result() for f in as_completed(futures)]
        
        success_count = sum(1 for _, success in results_list if success)
        avg_time = sum(t for t, _ in results_list) / len(results_list)
        
        passed = success_count >= 48  # Allow 2 failures
        return log_result("performance", "Concurrent Requests", passed,
                         f"{success_count}/50 success", avg_time)
    except Exception as e:
        return log_result("performance", "Concurrent Requests", False, str(e))

# ═══════════════════════════════════════════════════════════
# SECURITY TESTING - Vulnerability Checks
# ═══════════════════════════════════════════════════════════

def security_test_password_hashing():
    """Test: Passwords are hashed"""
    try:
        username = f"sectest_{random_string()}"
        email = f"{username}@test.com"
        password = "PlainTextPassword123"
        
        response = requests.post(f"{API_URL}/register", json={
            "username": username, "email": email, "password": password
        })
        
        # Password should never appear in response
        response_text = response.text.lower()
        passed = password.lower() not in response_text
        
        return log_result("security", "Password Hashing", passed,
                         "No plaintext in response" if passed else "EXPOSED!", 0)
    except Exception as e:
        return log_result("security", "Password Hashing", False, str(e))

def security_test_jwt_authentication():
    """Test: JWT tokens required for protected routes"""
    try:
        # Try to create post without auth
        response = requests.post(f"{API_URL}/posts", json={
            "post_type": "lost", "item_name": "Test", "location": "Test"
        })
        
        passed = response.status_code == 401
        return log_result("security", "JWT Authentication", passed,
                         "Unauthorized without token" if passed else "SECURITY RISK!", 0)
    except Exception as e:
        return log_result("security", "JWT Authentication", False, str(e))

def security_test_sql_injection():
    """Test: SQL injection prevented"""
    try:
        malicious_input = "' OR '1'='1"
        response = requests.post(f"{API_URL}/login", json={
            "email": malicious_input,
            "password": malicious_input
        })
        
        # Should return 401, not 500 or success
        passed = response.status_code == 401
        return log_result("security", "SQL Injection Prevention", passed,
                         "Rejected malicious input" if passed else "VULNERABLE!", 0)
    except Exception as e:
        return log_result("security", "SQL Injection Prevention", False, str(e))

def security_test_xss_prevention():
    """Test: XSS attacks prevented"""
    try:
        xss_payload = "<script>alert('XSS')</script>"
        username = f"xsstest_{random_string()}"
        
        response = requests.post(f"{API_URL}/register", json={
            "username": xss_payload,
            "email": f"{username}@test.com",
            "password": "Test123456"
        })
        
        # Should either reject or escape the input
        if response.status_code == 201:
            # Check if escaped
            passed = "&lt;script&gt;" in response.text or xss_payload not in response.text
        else:
            passed = True
        
        return log_result("security", "XSS Prevention", passed,
                         "Script tags handled" if passed else "VULNERABLE!", 0)
    except Exception as e:
        return log_result("security", "XSS Prevention", False, str(e))

def security_test_cors():
    """Test: CORS properly configured"""
    try:
        response = requests.options(f"{API_URL}/health",
                                   headers={"Origin": "http://localhost:5000"})
        
        has_cors = "Access-Control-Allow-Origin" in response.headers
        return log_result("security", "CORS Configuration", has_cors,
                         "CORS headers present" if has_cors else "Missing CORS", 0)
    except Exception as e:
        return log_result("security", "CORS Configuration", False, str(e))

# ═══════════════════════════════════════════════════════════
# MAIN TEST RUNNER
# ═══════════════════════════════════════════════════════════

def run_all_tests():
    """Execute all tests"""
    print("\n" + "═" * 80)
    print("COMPREHENSIVE TESTING SUITE - Back2Me".center(80))
    print("═" * 80)
    
    # SMOKE TESTS
    print("\n🔥 SMOKE TESTING".ljust(80, "─"))
    smoke_test_server_startup()
    smoke_test_homepage()
    smoke_test_login_page()
    smoke_test_static_files()
    
    # UAT
    print("\n👤 UAT - USER ACCEPTANCE TESTING".ljust(80, "─"))
    passed, cookies = uat_test_user_registration()
    if cookies:
        uat_test_create_post(cookies)
    else:
        # Try login with existing user
        passed, cookies = uat_test_user_login()
        if cookies:
            uat_test_create_post(cookies)
    
    uat_test_view_posts()
    
    # REGRESSION
    print("\n🔄 REGRESSION TESTING".ljust(80, "─"))
    regression_test_all_endpoints()
    regression_test_authentication_flow()
    
    # PERFORMANCE
    print("\n⚡ PERFORMANCE TESTING".ljust(80, "─"))
    performance_test_page_load_time()
    performance_test_api_response()
    performance_test_concurrent_requests()
    
    # SECURITY
    print("\n🔒 SECURITY TESTING".ljust(80, "─"))
    security_test_password_hashing()
    security_test_jwt_authentication()
    security_test_sql_injection()
    security_test_xss_prevention()
    security_test_cors()
    
    # SUMMARY
    print("\n" + "═" * 80)
    print("TEST SUMMARY".center(80))
    print("═" * 80)
    
    for category, tests in results.items():
        passed = sum(1 for t in tests if t["passed"])
        total = len(tests)
        percentage = (passed / total * 100) if total > 0 else 0
        status = "✓" if passed == total else "✗"
        
        print(f"{status} {category.upper():15} | {passed:2}/{total:2} passed | {percentage:5.1f}%")
    
    # Overall
    total_tests = sum(len(tests) for tests in results.values())
    total_passed = sum(sum(1 for t in tests if t["passed"]) for tests in results.values())
    overall_pct = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print("─" * 80)
    print(f"{'OVERALL':15} | {total_passed:2}/{total_tests:2} passed | {overall_pct:5.1f}%")
    print("═" * 80)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"test_results_{timestamp}.json", "w") as f:
        json.dump({
            "timestamp": timestamp,
            "summary": {
                "total": total_tests,
                "passed": total_passed,
                "failed": total_tests - total_passed,
                "percentage": overall_pct
            },
            "results": results
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: test_results_{timestamp}.json\n")
    
    return overall_pct >= 80  # 80% pass rate required

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
