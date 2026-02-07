import requests
import sys

BASE_URL = "http://localhost:8000"

def verify_create_user():
    # 1. Login as Chef
    print("1. Logging in as Chef...")
    resp = requests.post(f"{BASE_URL}/auth/token", data={"username": "chef", "password": "test123"})
    token = resp.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create New User via API
    print("\n2. Creating new user 'direct_hire'...")
    try:
        resp = requests.post(
            f"{BASE_URL}/users/",
            headers=headers,
            json={
                "username": "direct_hire",
                "password": "password123",
                "role": "Manager",
                "department": "Küche"
            }
        )
        if resp.status_code == 200:
            print("SUCCESS: User created successfully")
        elif resp.status_code == 400 and "Benutzername bereits vergeben" in resp.text:
             print("INFO: User already exists, continuing...")
        else:
             print(f"FAIL: Create failed: {resp.text}")
             return
    except Exception as e:
        print(f"FAIL: {e}")
        return

    # 3. Verify User Exists
    print("\n3. Verifying user exists...")
    resp = requests.get(f"{BASE_URL}/users/", headers=headers)
    users = resp.json()
    target_user = next((u for u in users if u['username'] == 'direct_hire'), None)
    
    if not target_user:
        print("FAIL: direct_hire not found")
        return
    
    print(f"Found User: {target_user['username']} ({target_user['role']} - {target_user['department']})")

    if target_user['role'] == "Manager" and target_user['department'] == "Küche":
        print("SUCCESS: properties match!")
    else:
        print("FAIL: properties do not match")

if __name__ == "__main__":
    verify_create_user()
