import requests
import sys

BASE_URL = "http://localhost:8000"

def verify_department_management():
    # 1. Login as Chef
    print("1. Logging in as Chef...")
    resp = requests.post(f"{BASE_URL}/auth/token", data={"username": "chef", "password": "test123"})
    token = resp.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}

    # 2. List Departments
    print("\n2. Initial List of Departments...")
    resp = requests.get(f"{BASE_URL}/departments/", headers=headers)
    depts = resp.json()
    print(f"Current Departments: {[d['name'] for d in depts]}")

    # 3. Create Department
    if not any(d['name'] == 'Bar' for d in depts):
        print("\n3. Creating Department 'Bar'...")
        resp = requests.post(f"{BASE_URL}/departments/", headers=headers, json={"name": "Bar"})
        if resp.status_code == 200:
            print("SUCCESS: Created 'Bar'")
        else:
            print(f"FAIL: {resp.text}")
    
    # 4. Verify Creation
    resp = requests.get(f"{BASE_URL}/departments/", headers=headers)
    new_depts = resp.json()
    bar = next((d for d in new_depts if d['name'] == 'Bar'), None)
    if bar:
        print(f"Verified 'Bar' exists with ID {bar['id']}")
    else:
        print("FAIL: 'Bar' not found")
        return

    # 5. Delete Department
    print(f"\n5. Deleting Department 'Bar' (ID: {bar['id']})...")
    resp = requests.delete(f"{BASE_URL}/departments/{bar['id']}", headers=headers)
    if resp.status_code == 200:
        print("SUCCESS: Deleted 'Bar'")
    else:
        print(f"FAIL: {resp.text}")
        return

    # 6. Verify Deletion
    resp = requests.get(f"{BASE_URL}/departments/", headers=headers)
    final_depts = resp.json()
    if not any(d['name'] == 'Bar' for d in final_depts):
        print("SUCCESS: 'Bar' is gone")
    else:
        print("FAIL: 'Bar' still exists")

if __name__ == "__main__":
    verify_department_management()
