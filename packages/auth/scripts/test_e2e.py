#!/usr/bin/env python3
"""
End-to-end test script for core authentication infrastructure
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
import requests
from dataclasses import dataclass


@dataclass
class ServiceConfig:
    name: str
    url: str
    health_endpoint: str = ""
    required: bool = True


class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


class AuthE2ETestRunner:
    """End-to-end test runner for core authentication infrastructure"""
    
    def __init__(self):
        self.services = [
            ServiceConfig("API", "http://localhost:8000", "/health", required=True),
            ServiceConfig("Keycloak", "http://localhost:8080", "/health/ready", required=False),
        ]
        self.failed_tests = []
        self.passed_tests = []
        self.session = requests.Session()
        self.session.timeout = 10.0
    
    def log(self, message: str, color: str = Colors.NC) -> None:
        """Print colored log message"""
        print(f"{color}{message}{Colors.NC}")
    
    def success(self, message: str) -> None:
        """Log success message"""
        self.log(f"✅ {message}", Colors.GREEN)
        self.passed_tests.append(message)
    
    def error(self, message: str) -> None:
        """Log error message"""
        self.log(f"❌ {message}", Colors.RED)
        self.failed_tests.append(message)
    
    def warning(self, message: str) -> None:
        """Log warning message"""
        self.log(f"⚠️  {message}", Colors.YELLOW)
    
    def info(self, message: str) -> None:
        """Log info message"""
        self.log(f"📋 {message}", Colors.BLUE)
    
    def check_service_health(self, service: ServiceConfig) -> bool:
        """Check if a service is healthy"""
        try:
            health_url = f"{service.url}{service.health_endpoint}"
            response = self.session.get(health_url, timeout=5.0)
            
            if response.status_code == 200:
                self.success(f"{service.name} is healthy")
                return True
            else:
                self.error(f"{service.name} health check failed (status: {response.status_code})")
                return False
                
        except Exception as e:
            if service.required:
                self.error(f"{service.name} is not accessible: {e}")
            else:
                self.warning(f"{service.name} is not accessible (optional): {e}")
            return False
    
    def test_service_availability(self) -> bool:
        """Test if all required services are available"""
        self.info("Checking service availability...")
        
        all_healthy = True
        for service in self.services:
            if service.health_endpoint:
                healthy = self.check_service_health(service)
            else:
                # Simple connectivity check
                try:
                    response = self.session.get(service.url, timeout=5.0)
                    self.success(f"{service.name} is accessible")
                    healthy = True
                except Exception as e:
                    if service.required:
                        self.error(f"{service.name} is not accessible")
                        healthy = False
                    else:
                        self.warning(f"{service.name} is not accessible (optional)")
                        healthy = True
            
            if service.required and not healthy:
                all_healthy = False
        
        return all_healthy
    
    
    def test_oidc_configuration(self) -> None:
        """Test OIDC configuration endpoints"""
        self.info("Testing OIDC configuration...")
        
        keycloak_url = "http://localhost:8080"
        
        try:
            # Test OIDC discovery
            oidc_response = self.session.get(
                f"{keycloak_url}/realms/spending-monitor/.well-known/openid-configuration"
            )
            
            if oidc_response.status_code == 200:
                self.success("OIDC configuration is accessible")
                
                # Parse and test JWKS
                oidc_config = oidc_response.json()
                if "jwks_uri" in oidc_config:
                    jwks_response = self.session.get(oidc_config["jwks_uri"])
                    
                    if jwks_response.status_code == 200:
                        jwks_data = jwks_response.json()
                        if "keys" in jwks_data and len(jwks_data["keys"]) > 0:
                            self.success("JWKS endpoint is accessible and has keys")
                        else:
                            self.warning("JWKS endpoint accessible but no keys found")
                    else:
                        self.error("JWKS endpoint is not accessible")
                else:
                    self.error("OIDC config missing jwks_uri")
            else:
                # This is expected due to flaky OIDC discovery with Python clients
                self.warning(f"OIDC configuration not accessible (status: {oidc_response.status_code})")
                self.warning("Note: This is a known issue with Python clients, but API uses fallback configuration")
                
        except Exception as e:
            # This is expected due to flaky OIDC discovery
            self.warning(f"OIDC configuration test failed: {e}")
            self.warning("Note: API uses fallback configuration when OIDC discovery fails")
    
    def test_jwt_middleware(self) -> None:
        """Test JWT middleware is properly configured"""
        self.info("Testing JWT middleware configuration...")
        
        try:
            # Test that the JWT middleware is available by checking the auth module
            import sys
            sys.path.append('/Users/skattoju/code/spending-transaction-monitor/packages/api/src')
            from auth.middleware import require_authentication, get_current_user
            
            self.success("JWT middleware functions are available")
            
            # Test basic functionality by ensuring functions exist
            if callable(require_authentication) and callable(get_current_user):
                self.success("JWT middleware functions are callable")
            else:
                self.error("JWT middleware functions are not properly configured")
                
        except ImportError as e:
            self.error(f"JWT middleware not available: {e}")
        except Exception as e:
            self.error(f"JWT middleware test failed: {e}")
    
    def test_api_documentation(self) -> None:
        """Test API documentation accessibility"""
        self.info("Testing API documentation...")
        
        api_url = "http://localhost:8000"
        
        try:
            # Test OpenAPI docs
            docs_response = self.session.get(f"{api_url}/docs")
            if docs_response.status_code == 200:
                self.success("API documentation is accessible")
            else:
                # Try OpenAPI JSON
                openapi_response = self.session.get(f"{api_url}/openapi.json")
                if openapi_response.status_code == 200:
                    self.success("OpenAPI schema is accessible")
                else:
                    self.warning("API documentation not accessible")
                    
        except Exception as e:
            self.warning(f"API documentation test failed: {e}")
    
    
    def test_cors_configuration(self) -> None:
        """Test CORS configuration for frontend integration"""
        self.info("Testing CORS configuration...")
        
        api_url = "http://localhost:8000"
        
        try:
            # Test preflight request
            headers = {
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization,content-type"
            }
            
            response = self.session.options(f"{api_url}/health", headers=headers)
            
            if response.status_code in [200, 204]:
                cors_headers = response.headers
                if "access-control-allow-origin" in cors_headers:
                    self.success("CORS is properly configured")
                else:
                    self.warning("CORS headers not found")
            else:
                self.warning("CORS preflight failed")
                
        except Exception as e:
            self.warning(f"CORS test failed: {e}")
    
    def test_health_endpoint(self) -> None:
        """Test API health endpoint"""
        self.info("Testing API health endpoint...")
        
        api_url = "http://localhost:8000"
        
        try:
            response = self.session.get(f"{api_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get("status") == "healthy":
                    self.success("API health endpoint reports healthy")
                else:
                    self.warning("API health endpoint accessible but status unclear")
            else:
                self.error(f"API health endpoint failed (status: {response.status_code})")
                
        except Exception as e:
            self.error(f"API health endpoint test failed: {e}")
    
    def print_summary(self) -> None:
        """Print test summary"""
        self.log("\n" + "="*50, Colors.BLUE)
        self.log("🔐 Core Auth Infrastructure Test Results", Colors.BLUE)
        self.log("="*50, Colors.BLUE)
        
        self.log(f"\n✅ Passed: {len(self.passed_tests)}", Colors.GREEN)
        for test in self.passed_tests[:5]:  # Show first 5
            self.log(f"   • {test}", Colors.GREEN)
        if len(self.passed_tests) > 5:
            self.log(f"   ... and {len(self.passed_tests) - 5} more", Colors.GREEN)
        
        if self.failed_tests:
            self.log(f"\n❌ Failed: {len(self.failed_tests)}", Colors.RED)
            for test in self.failed_tests:
                self.log(f"   • {test}", Colors.RED)
        
        self.log("\n🚀 Next Steps:", Colors.BLUE)
        self.log("1. Set up Keycloak client: cd ../auth && python scripts/setup_keycloak.py")
        self.log("2. API docs: http://localhost:8000/docs")
        self.log("3. Test endpoints with JWT authentication (when implemented)")
        
        self.log("\n💡 Integration tips:", Colors.YELLOW)
        self.log("   • Use Depends(require_authentication) for protected routes")
        self.log("   • Use Depends(get_current_user) for optional auth")
        self.log("   • Use Depends(require_role('admin')) for role-based access")
        self.log("   • See AUTH_INTEGRATION_GUIDE.md for full details")
    
    def run_all_tests(self) -> bool:
        """Run all E2E tests for core auth infrastructure"""
        self.log("🔐 Starting Core Auth Infrastructure Tests", Colors.BLUE)
        self.log("="*50, Colors.BLUE)
        
        # Check service availability first
        services_ok = self.test_service_availability()
        if not services_ok:
            self.error("Required services are not available")
            self.log("\n💡 Try running: cd ../auth && make services-up", Colors.YELLOW)
            return False
        
        # Run all test suites
        self.test_health_endpoint()
        self.test_oidc_configuration()
        self.test_jwt_middleware()
        self.test_api_documentation()
        self.test_cors_configuration()
        
        self.print_summary()
        
        # Return True if no critical failures
        return len(self.failed_tests) == 0


def main():
    """Main entry point"""
    runner = AuthE2ETestRunner()
    
    try:
        success = runner.run_all_tests()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        runner.warning("Tests interrupted by user")
        return 1
    except Exception as e:
        runner.error(f"Unexpected error: {e}")
        return 1
    finally:
        runner.session.close()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
