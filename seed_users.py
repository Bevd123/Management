import requests

BASE_URL = "http://localhost:8000"

# Test users to create
test_users = [
    {
        "username": "koch1",
        "password": "test123",
        "role": "Mitarbeiter",
        "department": "Küche"
    },
    {
        "username": "kellner1",
        "password": "test123",
        "role": "Mitarbeiter",
        "department": "Service"
    },
    {
        "username": "manager_service",
        "password": "test123",
        "role": "Manager",
        "department": "Service"
    },
    {
        "username": "manager_kueche",
        "password": "test123",
        "role": "Manager",
        "department": "Küche"
    },
    {
        "username": "chef",
        "password": "test123",
        "role": "Geschäftsführer",
        "department": "Management"
    }
]

print("Creating test users...")
for user in test_users:
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user)
        if response.status_code == 200:
            print(f"✓ Created user: {user['username']} ({user['role']}, {user['department']})")
        else:
            print(f"✗ Failed to create {user['username']}: {response.text}")
    except Exception as e:
        print(f"✗ Error creating {user['username']}: {e}")

print("\nTest users created! You can now log in with:")
print("- koch1 / test123 (Mitarbeiter, Küche)")
print("- kellner1 / test123 (Mitarbeiter, Service)")
print("- manager_service / test123 (Manager, Service)")
print("- manager_kueche / test123 (Manager, Küche)")
print("- chef / test123 (Geschäftsführer, Management)")
