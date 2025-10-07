#!/usr/bin/env python3
"""
Sync database users with Keycloak users
"""

import requests
import json
import csv

# Get admin token
admin_url = "http://localhost:8080/realms/master/protocol/openid-connect/token"
admin_data = {
    "username": "admin",
    "password": "admin",
    "grant_type": "password",
    "client_id": "admin-cli",
}

response = requests.post(admin_url, data=admin_data)
if response.status_code != 200:
    print(f"Failed to get admin token: {response.status_code}")
    exit(1)

access_token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {access_token}"}

# Read the sample users CSV
users = []
with open('../../data/sample_users.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        users.append(row)

print(f"Found {len(users)} users in database")

# Create Keycloak users for the first few users
test_users = users[:3]  # Let's create the first 3 users for testing

for user in test_users:
    user_id = user['id']
    email = user['email']
    first_name = user['first_name']
    last_name = user['last_name']
    keycloak_id = user['keycloak_id']
    
    print(f"\nCreating Keycloak user for {email} (DB ID: {user_id})")
    
    # Create user in Keycloak
    user_data = {
        "id": keycloak_id,  # Use the existing keycloak_id from database
        "username": email.split('@')[0],  # Use email prefix as username
        "email": email,
        "firstName": first_name,
        "lastName": last_name,
        "enabled": True,
        "emailVerified": True,
        "credentials": [
            {"type": "password", "value": "password123", "temporary": False}
        ],
        "requiredActions": [],
        "attributes": {
            "locale": ["en"],
            "db_user_id": [user_id]  # Store the database user ID
        }
    }
    
    users_url = "http://localhost:8080/admin/realms/spending-monitor/users"
    response = requests.post(users_url, json=user_data, headers=headers)
    
    if response.status_code == 201:
        print(f"✅ Created Keycloak user: {email}")
        
        # Assign user role
        role_url = f"http://localhost:8080/admin/realms/spending-monitor/roles/user"
        role_response = requests.get(role_url, headers=headers)
        
        if role_response.status_code == 200:
            role_data = role_response.json()
            assign_url = f"http://localhost:8080/admin/realms/spending-monitor/users/{keycloak_id}/role-mappings/realm"
            assign_response = requests.post(assign_url, json=[role_data], headers=headers)
            
            if assign_response.status_code == 204:
                print(f"✅ Assigned user role to {email}")
                
                # Test token generation
                token_url = "http://localhost:8080/realms/spending-monitor/protocol/openid-connect/token"
                token_data = {
                    "grant_type": "password",
                    "client_id": "spending-monitor",
                    "username": email,
                    "password": "password123"
                }
                
                token_response = requests.post(token_url, data=token_data)
                if token_response.status_code == 200:
                    token_info = token_response.json()
                    user_token = token_info["access_token"]
                    print(f"✅ Token generation successful for {email}")
                    print(f"   Token: {user_token[:50]}...")
                    
                    # Test with API
                    api_url = "http://localhost:8000/api/users/"
                    api_headers = {"Authorization": f"Bearer {user_token}"}
                    
                    api_response = requests.get(api_url, headers=api_headers)
                    print(f"   API test status: {api_response.status_code}")
                    
                else:
                    print(f"❌ Token generation failed for {email}: {token_response.status_code}")
                    print(f"   Response: {token_response.text}")
            else:
                print(f"❌ Failed to assign role to {email}: {assign_response.status_code}")
        else:
            print(f"❌ Failed to get role: {role_response.status_code}")
    else:
        print(f"❌ Failed to create user {email}: {response.status_code}")
        if response.text:
            print(f"   Response: {response.text}")

print(f"\n🎉 Created {len(test_users)} test users from database!")
print("\n📋 Test User Credentials:")
print("=" * 50)
for user in test_users:
    print(f"Email: {user['email']}")
    print(f"Password: password123")
    print(f"Database ID: {user['id']}")
    print(f"Name: {user['first_name']} {user['last_name']}")
    print("-" * 30)
