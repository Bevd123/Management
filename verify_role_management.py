import requests
import sys

BASE_URL = "http://localhost:8000"

def verify_role_management():
    # 1. Register new user (should be Pending)
    print("1. Registering new user 'new_hire'...")
    resp = requests.post(f"{BASE_URL}/auth/register", json={"username": "new_hire", "password": "password123"})
    if resp.status_code != 200:
        print(f"Failed to register: {resp.text}")
        return
    user_data = resp.json()
    print(f"Created user: {user_data['username']} (Role: {user_data['role']}, Dept: {user_data['department']})")

    if user_data['role'] != 'Pending':
        print("FAIL: Role is not Pending")
        return

    # 2. Login as Chef
    print("\n2. Logging in as Chef...")
    resp = requests.post(f"{BASE_URL}/auth/token", data={"username": "chef", "password": "test123"})
    token = resp.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}

    # 3. List users
    print("\n3. Listing users...")
    resp = requests.get(f"{BASE_URL}/users/", headers=headers)
    users = resp.json()
    target_user = next((u for u in users if u['username'] == 'new_hire'), None)
    
    if not target_user:
        print("FAIL: new_hire not found in list")
        return
    print(f"Found new_hire: ID={target_user['id']}, Role={target_user['role']}")

    # 4. Assign Role
    print(f"\n4. Assigning Role 'Mitarbeiter' / 'Service' to ID {target_user['id']}...")
    resp = requests.put(
        f"{BASE_URL}/users/{target_user['id']}/role",
        headers=headers,
        json={"role": "Mitarbeiter", "department": "Service"}
    )
    
    if resp.status_code != 200:
        print(f"FAIL: Update failed: {resp.text}")
        return
    
    updated_user = resp.json()
    print(f"Updated User: {updated_user['username']} -> {updated_user['role']} / {updated_user['department']}")

    if updated_user['role'] == "Mitarbeiter" and updated_user['department'] == "Service":
        print("\nSUCCESS: Role assignment flow verified!")
    else:
        print("\nFAIL: Role/Department mismatch")

if __name__ == "__main__":
    verify_role_management()
