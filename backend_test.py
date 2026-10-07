#!/usr/bin/env python3
"""
Backend smoke test for GiftsDates authentication flow.
Tests: health check, register, login, and authenticated /me endpoint.
"""
import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://giftsdate-saver.preview.emergentagent.com/api"

def log(msg):
    """Print timestamped log message."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def test_health_check():
    """Test GET /api/ returns service info."""
    log("Testing health check endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        log(f"  Status: {response.status_code}")
        
        if response.status_code != 200:
            log(f"  ❌ FAILED: Expected 200, got {response.status_code}")
            return False
        
        data = response.json()
        log(f"  Response: {json.dumps(data, indent=2)}")
        
        # Check for expected fields
        if data.get("service") == "GiftsDates" and data.get("ok") is True:
            log("  ✅ PASSED: Health check successful")
            return True
        else:
            log(f"  ❌ FAILED: Unexpected response format")
            return False
            
    except Exception as e:
        log(f"  ❌ FAILED: {str(e)}")
        return False

def test_register():
    """Test POST /api/auth/register creates a new user."""
    log("Testing user registration...")
    
    # Generate unique email for this test run
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_user = {
        "email": f"testuser_{timestamp}@example.com",
        "password": "SecurePass123!",
        "name": "Test User",
        "age": 28,
        "gender": "female",
        "interested_in": "male",
        "orientation": "straight",
        "city": "New York",
        "country": "USA",
        "bio": "Test user for smoke testing",
        "birth_year": 1996,
        "birth_month": 5,
        "birth_day": 15
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json=test_user,
            timeout=10
        )
        log(f"  Status: {response.status_code}")
        
        if response.status_code != 200:
            log(f"  ❌ FAILED: Expected 200, got {response.status_code}")
            log(f"  Response: {response.text}")
            return False, None, None
        
        data = response.json()
        
        # Check for token and user in response
        if "token" not in data or "user" not in data:
            log(f"  ❌ FAILED: Missing token or user in response")
            log(f"  Response: {json.dumps(data, indent=2)}")
            return False, None, None
        
        token = data["token"]
        user = data["user"]
        
        log(f"  ✅ PASSED: User registered successfully")
        log(f"  User ID: {user.get('id')}")
        log(f"  Email: {user.get('email')}")
        log(f"  Token: {token[:20]}...")
        
        return True, test_user, token
        
    except Exception as e:
        log(f"  ❌ FAILED: {str(e)}")
        return False, None, None

def test_login(email, password):
    """Test POST /api/auth/login with credentials."""
    log("Testing user login...")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        log(f"  Status: {response.status_code}")
        
        if response.status_code != 200:
            log(f"  ❌ FAILED: Expected 200, got {response.status_code}")
            log(f"  Response: {response.text}")
            return False, None
        
        data = response.json()
        
        # Check for token in response
        if "token" not in data:
            log(f"  ❌ FAILED: Missing token in response")
            log(f"  Response: {json.dumps(data, indent=2)}")
            return False, None
        
        token = data["token"]
        
        log(f"  ✅ PASSED: Login successful")
        log(f"  Token: {token[:20]}...")
        
        return True, token
        
    except Exception as e:
        log(f"  ❌ FAILED: {str(e)}")
        return False, None

def test_authenticated_me(token):
    """Test GET /api/auth/me with JWT token."""
    log("Testing authenticated /me endpoint...")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        log(f"  Status: {response.status_code}")
        
        if response.status_code != 200:
            log(f"  ❌ FAILED: Expected 200, got {response.status_code}")
            log(f"  Response: {response.text}")
            return False
        
        data = response.json()
        
        # Check for user data
        if "id" not in data or "email" not in data:
            log(f"  ❌ FAILED: Missing user data in response")
            log(f"  Response: {json.dumps(data, indent=2)}")
            return False
        
        log(f"  ✅ PASSED: Authenticated request successful")
        log(f"  User ID: {data.get('id')}")
        log(f"  Email: {data.get('email')}")
        log(f"  Name: {data.get('name')}")
        
        return True
        
    except Exception as e:
        log(f"  ❌ FAILED: {str(e)}")
        return False

def test_bust_type_field(token):
    """Test bust_type field persistence via PATCH and GET /api/auth/me."""
    log("Testing bust_type field round-trip...")
    
    try:
        # Step 1: PATCH with bust_type = "natural"
        log("  Step 1: Setting bust_type to 'natural'...")
        response = requests.patch(
            f"{BACKEND_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"bust_type": "natural"},
            timeout=10
        )
        log(f"    Status: {response.status_code}")
        
        if response.status_code != 200:
            log(f"    ❌ FAILED: Expected 200, got {response.status_code}")
            log(f"    Response: {response.text}")
            return False
        
        data = response.json()
        if data.get("bust_type") != "natural":
            log(f"    ❌ FAILED: PATCH response bust_type is '{data.get('bust_type')}', expected 'natural'")
            return False
        log(f"    ✅ PATCH successful, bust_type set to 'natural'")
        
        # Step 2: GET to verify bust_type = "natural"
        log("  Step 2: Verifying bust_type is 'natural' via GET...")
        response = requests.get(
            f"{BACKEND_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        log(f"    Status: {response.status_code}")
        
        if response.status_code != 200:
            log(f"    ❌ FAILED: Expected 200, got {response.status_code}")
            log(f"    Response: {response.text}")
            return False
        
        data = response.json()
        if data.get("bust_type") != "natural":
            log(f"    ❌ FAILED: GET response bust_type is '{data.get('bust_type')}', expected 'natural'")
            return False
        log(f"    ✅ GET confirmed bust_type is 'natural'")
        
        # Step 3: PATCH with bust_type = "enhanced"
        log("  Step 3: Updating bust_type to 'enhanced'...")
        response = requests.patch(
            f"{BACKEND_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"bust_type": "enhanced"},
            timeout=10
        )
        log(f"    Status: {response.status_code}")
        
        if response.status_code != 200:
            log(f"    ❌ FAILED: Expected 200, got {response.status_code}")
            log(f"    Response: {response.text}")
            return False
        
        data = response.json()
        if data.get("bust_type") != "enhanced":
            log(f"    ❌ FAILED: PATCH response bust_type is '{data.get('bust_type')}', expected 'enhanced'")
            return False
        log(f"    ✅ PATCH successful, bust_type updated to 'enhanced'")
        
        # Step 4: GET to verify bust_type = "enhanced"
        log("  Step 4: Verifying bust_type is 'enhanced' via GET...")
        response = requests.get(
            f"{BACKEND_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        log(f"    Status: {response.status_code}")
        
        if response.status_code != 200:
            log(f"    ❌ FAILED: Expected 200, got {response.status_code}")
            log(f"    Response: {response.text}")
            return False
        
        data = response.json()
        if data.get("bust_type") != "enhanced":
            log(f"    ❌ FAILED: GET response bust_type is '{data.get('bust_type')}', expected 'enhanced'")
            return False
        log(f"    ✅ GET confirmed bust_type is 'enhanced'")
        
        log("  ✅ PASSED: bust_type field persists correctly through PATCH and GET")
        return True
        
    except Exception as e:
        log(f"  ❌ FAILED: {str(e)}")
        return False

def main():
    """Run all authentication smoke tests."""
    log("=" * 60)
    log("GiftsDates Backend Authentication Smoke Test")
    log("=" * 60)
    log(f"Backend URL: {BACKEND_URL}")
    log("")
    
    results = {
        "health_check": False,
        "register": False,
        "login": False,
        "authenticated_me": False,
        "bust_type_field": False
    }
    
    # Test 1: Health check
    results["health_check"] = test_health_check()
    log("")
    
    # Test 2: Register new user
    register_success, test_user, register_token = test_register()
    results["register"] = register_success
    log("")
    
    if not register_success:
        log("⚠️  Skipping remaining tests due to registration failure")
        print_summary(results)
        return 1
    
    # Test 3: Login with same credentials
    login_success, login_token = test_login(test_user["email"], test_user["password"])
    results["login"] = login_success
    log("")
    
    if not login_success:
        log("⚠️  Skipping authenticated test due to login failure")
        print_summary(results)
        return 1
    
    # Test 4: Authenticated /me endpoint
    results["authenticated_me"] = test_authenticated_me(login_token)
    log("")
    
    # Test 5: bust_type field persistence
    results["bust_type_field"] = test_bust_type_field(login_token)
    log("")
    
    # Print summary
    print_summary(results)
    
    # Return exit code
    return 0 if all(results.values()) else 1

def print_summary(results):
    """Print test summary."""
    log("=" * 60)
    log("TEST SUMMARY")
    log("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        log(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log("")
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    log(f"Total: {passed_count}/{total_count} tests passed")
    log("=" * 60)

if __name__ == "__main__":
    sys.exit(main())
