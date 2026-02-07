import requests
import sys

BASE_URL = "http://localhost:8000"

def verify_full_user_edit():
    # 1. Login as Chef
    print("1. Logging in as Chef...")
    resp = requests.post(f"{BASE_URL}/auth/token", data={"username": "chef", "password": "test123"})
    token = resp.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get new_hire User
    print("\n2. Finding user 'new_hire'...")
    resp = requests.get(f"{BASE_URL}/users/", headers=headers)
    users = resp.json()
    target_user = next((u for u in users if u['username'] == 'new_hire'), None)
    
    if not target_user:
        # Create user if not exists
        requests.post(f"{BASE_URL}/auth/register", json={"username": "new_hire", "password": "password123"})
        # Re-fetch
        resp = requests.get(f"{BASE_URL}/users/", headers=headers)
        users = resp.json()
        target_user = next((u for u in users if u['username'] == 'new_hire'), None)
        if not target_user:
            print("FAIL: Could not find or create user")
            # Try finding 'renamed_user' and rename back just in case
            target_user = next((u for u in users if u['username'] == 'renamed_user'), None)
            if target_user:
                 print("Found 'renamed_user' instead, will reuse.")
            else: 
                 return

    print(f"Found User: {target_user['username']} (ID: {target_user['id']})")

    # 3. Update Username and Password
    print(f"\n3. Updating Username to 'renamed_user' and Password to 'newpass123'...")
    resp = requests.put(
        f"{BASE_URL}/users/{target_user['id']}",
        headers=headers,
        json={
            "role": target_user['role'],
            "department": target_user['department'],
            "username": "renamed_user",
            "password": "newpass123"
        }
    )

    if resp.status_code != 200:
        print(f"FAIL: Update failed: {resp.text}")
        return
    
    updated_user = resp.json()
    print(f"Updated User: {updated_user['username']}")

    if updated_user['username'] != "renamed_user":
        print("FAIL: Username not updated")
        return

    # 4. Verify Login with New Password
    print("\n4. Verifying Login with new credentials...")
    resp = requests.post(f"{BASE_URL}/auth/token", data={"username": "renamed_user", "password": "newpass123"})
    if resp.status_code == 200:
        print("SUCCESS: Login successful with new username and password!")
    else:
        print(f"FAIL: Login failed: {resp.text}")

if __name__ == "__main__":
    verify_full_user_edit()
