from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas, auth

router = APIRouter(
    prefix="/departments",
    tags=["departments"],
    responses={404: {"detail": "Not found"}},
)

@router.get("/", response_model=List[schemas.Department])
def read_departments(skip: int = 0, limit: int = 100, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    departments = crud.get_departments(db, skip=skip, limit=limit)
    return departments

@router.post("/", response_model=schemas.Department)
def create_department(department: schemas.DepartmentCreate, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    if current_user.role != "Geschäftsführer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur der Geschäftsführer kann Abteilungen erstellen"
        )
    return crud.create_department(db=db, department=department)

@router.put("/{department_id}", response_model=schemas.Department)
def update_department(department_id: int, department: schemas.DepartmentUpdate, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    if current_user.role != "Geschäftsführer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur der Geschäftsführer kann Abteilungen bearbeiten"
        )
    
    updated_dept = crud.update_department(db, department_id, department)
    if updated_dept is None:
        raise HTTPException(status_code=404, detail="Department not found")
    if updated_dept is False:
        raise HTTPException(status_code=400, detail="Department name already exists")
        
    return updated_dept

@router.delete("/{department_id}")
def delete_department(department_id: int, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    if current_user.role != "Geschäftsführer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur der Geschäftsführer kann Abteilungen löschen"
        )
    success = crud.delete_department(db, department_id)
    if not success:
        raise HTTPException(status_code=404, detail="Department not found")
    return {"ok": True}
