from sqlalchemy.orm import Session
from . import models, schemas
import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    
    # Determine role/dept based on schema type
    role = "Pending"
    department = None
    if hasattr(user, "role"):
        role = user.role
    if hasattr(user, "department"):
        department = user.department

    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        role=role,
        department=department,
        inventory={}
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Department CRUD
def get_departments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Department).offset(skip).limit(limit).all()

def create_department(db: Session, department: schemas.DepartmentCreate):
    db_department = models.Department(name=department.name)
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

def delete_department(db: Session, department_id: int):
    department = db.query(models.Department).filter(models.Department.id == department_id).first()
    if department:
        db.delete(department)
        db.commit()
        return True
    return False

def update_department(db: Session, department_id: int, department_update: schemas.DepartmentUpdate):
    db_dept = db.query(models.Department).filter(models.Department.id == department_id).first()
    if not db_dept:
        return None
    
    old_name = db_dept.name
    new_name = department_update.name
    
    if old_name != new_name:
        # Check if new name exists
        existing = db.query(models.Department).filter(models.Department.name == new_name).first()
        if existing:
            return False # Collision
            
        # Update Department
        db_dept.name = new_name
        
        # Update Users (Constraint: "Hardcoded" strings in User table)
        db.query(models.User).filter(models.User.department == old_name).update(
            {"department": new_name}, synchronize_session=False
        )
        
        db.commit()
        db.refresh(db_dept)
    
    return db_dept
