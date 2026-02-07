from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, models, schemas, auth

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: Annotated[schemas.User, Depends(auth.get_current_user)]):
    return current_user

@router.get("/", response_model=List[schemas.User])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(auth.get_db), 
    current_user: schemas.User = Depends(auth.get_current_user)
):
    # Permission Logic
    if current_user.role == "Geschäftsführer":
        # CEO sees all
        return db.query(models.User).offset(skip).limit(limit).all()
    
    if current_user.role == "Manager":
        # Managers see only their department
        return db.query(models.User).filter(models.User.department == current_user.department).offset(skip).limit(limit).all()
    
    # Employees and Pending users see nothing (or maybe empty list)
    return []

@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdateAdmin,
    db: Session = Depends(auth.get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    if current_user.role != "Geschäftsführer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur der Geschäftsführer kann Benutzer bearbeiten"
        )
    
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    
    # Update Role and Department
    db_user.role = user_update.role
    db_user.department = user_update.department

    # Update Username if provided and different
    if user_update.username and user_update.username != db_user.username:
        # Check if username exists
        existing_user = crud.get_user_by_username(db, username=user_update.username)
        if existing_user:
             raise HTTPException(status_code=400, detail="Benutzername bereits vergeben")
        db_user.username = user_update.username

    # Update Password if provided
    if user_update.password:
        db_user.hashed_password = crud.get_password_hash(user_update.password)

    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/", response_model=schemas.User)
def create_user_admin(
    user: schemas.UserCreateAdmin,
    db: Session = Depends(auth.get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    if current_user.role != "Geschäftsführer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur der Geschäftsführer kann neue Benutzer anlegen"
        )
    
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Benutzername bereits vergeben")
    
    return crud.create_user(db=db, user=user)
