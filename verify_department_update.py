import requests
import sys

BASE_URL = "http://localhost:8000"

def verify_department_update():
    # 1. Login as Chef
    print("1. Logging in as Chef...")
    resp = requests.post(f"{BASE_URL}/auth/token", data={"username": "chef", "password": "test123"})
    token = resp.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Setup: Create Dept "TestDept" and User "TestUser"
    print("\n2. Setup: Creating Dept 'TestDept' and User 'TestUser'...")
    requests.post(f"{BASE_URL}/departments/", headers=headers, json={"name": "TestDept"})
    requests.post(f"{BASE_URL}/users/", headers=headers, json={
        "username": "dept_test_user", "password": "pw", "role": "Mitarbeiter", "department": "TestDept"
    })

    # 3. Verify User Dept
    print("3. Verifying initial user dept...")
    resp = requests.get(f"{BASE_URL}/users/", headers=headers)
    users = resp.json()
    user = next((u for u in users if u['username'] == 'dept_test_user'), None)
    print(f"User Dept: {user['department']}")
    if user['department'] != "TestDept":
        print("FAIL: Setup failed")
        return

    # 4. Rename Department
    print("\n4. Renaming 'TestDept' to 'RenamedDept'...")
    # Find ID first
    resp = requests.get(f"{BASE_URL}/departments/", headers=headers)
    dept_id = next(d['id'] for d in resp.json() if d['name'] == 'TestDept')
    
    resp = requests.put(f"{BASE_URL}/departments/{dept_id}", headers=headers, json={"name": "RenamedDept"})
    if resp.status_code == 200:
        print("SUCCESS: Renamed")
    else:
        print(f"FAIL: {resp.text}")
        return

    # 5. Verify User Dept Updated
    print("\n5. Verifying user dept updated...")
    resp = requests.get(f"{BASE_URL}/users/", headers=headers)
    users = resp.json()
    user = next((u for u in users if u['username'] == 'dept_test_user'), None)
    print(f"User Dept: {user['department']}")
    
    if user['department'] == "RenamedDept":
        print("SUCCESS: User cascade update worked!")
    else:
        print("FAIL: User dept not updated")

    # Cleanup
    requests.delete(f"{BASE_URL}/departments/{dept_id}", headers=headers)

if __name__ == "__main__":
    verify_department_update()
