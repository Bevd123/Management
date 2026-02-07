import sys
sys.path.insert(0, '/home/rap/API')

from backend.database import SessionLocal, Base, engine
from backend import models, schemas, crud

# Recreate tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Create test users
db = SessionLocal()

# Create departments
departments = ["Service", "Küche", "Management"]
for dept_name in departments:
    try:
        db_dept = models.Department(name=dept_name)
        db.add(db_dept)
        db.commit()
        print(f"✓ Created Department: {dept_name}")
    except Exception:
        db.rollback()
        print(f"⚠ Department {dept_name} already exists")

test_users = [
    {"username": "chef", "password": "test123", "role": "Geschäftsführer", "department": "Management"},
    {"username": "manager_service", "password": "test123", "role": "Manager", "department": "Service"},
    {"username": "manager_kueche", "password": "test123", "role": "Manager", "department": "Küche"},
    {"username": "kellner1", "password": "test123", "role": "Mitarbeiter", "department": "Service"},
    {"username": "koch1", "password": "test123", "role": "Mitarbeiter", "department": "Küche"},
]

for user_data in test_users:
    # Hash password directly
    hashed_pw = crud.get_password_hash(user_data["password"])
    
    # Create user model directly to bypass "Pending" default in crud.create_user
    db_user = models.User(
        username=user_data["username"],
        hashed_password=hashed_pw,
        role=user_data["role"],
        department=user_data["department"],
        inventory={}
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        print(f"✓ Created: {db_user.username} ({db_user.role}, {db_user.department})")
    except Exception as e:
        db.rollback()
        print(f"✗ Failed to create {user_data['username']}: {e}")

db.close()
print("\nTest users created successfully!")
