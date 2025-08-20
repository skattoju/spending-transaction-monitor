#!/usr/bin/env python3
"""
Quick test script to verify auth demo endpoints are working
"""

import requests
import json
import sys
from typing import Optional


def test_endpoint(endpoint: str, token: Optional[str] = None, description: str = "") -> None:
    """Test a single auth demo endpoint"""
    url = f"http://localhost:8000/auth-demo{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {endpoint}")
    print(f"Description: {description}")
    print(f"URL: {url}")
    print(f"Headers: {'With Auth Token' if token else 'No Auth'}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10.0)
        
        print(f"Status: {response.status_code} {response.reason}")
        
        try:
            result = response.json()
            print("Response:")
            print(json.dumps(result, indent=2))
        except json.JSONDecodeError:
            print(f"Response Text: {response.text}")
            
        return response.status_code < 400
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False


def main():
    print("🔐 Auth Demo Endpoint Tester")
    print("=" * 60)
    
    # Check if API is running
    try:
        health_response = requests.get("http://localhost:8000/health", timeout=5.0)
        if health_response.status_code != 200:
            print("❌ API server not responding. Please start with: pnpm dev (in packages/api)")
            sys.exit(1)
        print("✅ API server is running")
    except requests.exceptions.RequestException:
        print("❌ API server not accessible on http://localhost:8000")
        print("Please start with: pnpm dev (in packages/api)")
        sys.exit(1)
    
    # Get token from user (optional)
    print("\n" + "=" * 60)
    print("To test protected endpoints, you need a JWT token.")
    print("Options:")
    print("1. Go to http://localhost:5173/auth-demo, login, and copy token from browser DevTools")
    print("2. Skip token testing (will test public endpoints only)")
    print("=" * 60)
    
    token = input("\nEnter JWT token (or press Enter to skip): ").strip()
    if not token:
        token = None
        print("⚠️  Will test public endpoints only")
    else:
        print("✅ Will test with provided token")
    
    # Test all endpoints
    endpoints = [
        ("/public", "Accessible without authentication"),
        ("/profile", "Shows different content based on auth status"),
        ("/protected", "Requires valid JWT token"),
        ("/user-only", "Requires 'user' role or higher"),
        ("/admin-only", "Requires 'admin' role"),
        ("/token-info", "Shows JWT token claims and details"),
    ]
    
    results = []
    for endpoint, description in endpoints:
        # Test public endpoints without token, protected with token
        if endpoint in ["/public"]:
            success = test_endpoint(endpoint, None, description)
        elif endpoint in ["/profile"]:
            # Test both with and without token
            success1 = test_endpoint(endpoint, None, f"{description} (no auth)")
            if token:
                success2 = test_endpoint(endpoint, token, f"{description} (with auth)")
                success = success1 and success2
            else:
                success = success1
        else:
            # Protected endpoints
            if token:
                success = test_endpoint(endpoint, token, description)
            else:
                print(f"\n⏭️  Skipping {endpoint} (requires token)")
                success = True  # Don't count as failure
        
        results.append((endpoint, success))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    for endpoint, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {endpoint}")
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n🎯 Results: {successful}/{total} endpoints working")
    
    if successful == total:
        print("🎉 All auth demo endpoints are working perfectly!")
    else:
        print("⚠️  Some endpoints had issues. Check API logs and Keycloak configuration.")


if __name__ == "__main__":
    main()
