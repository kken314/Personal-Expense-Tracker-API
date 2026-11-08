from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas
import auth_utils

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.get('/', response_model=List[schemas.CategoryResponse])
def get_all_categories(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    categories = db.query(models.Category).filter(models.Category.user_id == current_user.id).all()
    return categories

@router.get('/{id}', response_model=schemas.CategoryResponse)
def get_category(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    category = db.query(models.Category).filter(
        models.Category.id == id,
        models.Category.user_id == current_user.id
    ).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category

@router.post('/', response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    existing_category = db.query(models.Category).filter(
        models.Category.name == category.name,
        models.Category.user_id == current_user.id
    ).first()
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )

    new_category = models.Category(
        name=category.name,
        user_id=current_user.id
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return new_category

@router.put('/{id}', response_model=schemas.CategoryResponse)
def update_category(
    id: int,
    category: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    db_category = db.query(models.Category).filter(
        models.Category.id == id,
        models.Category.user_id == current_user.id
    ).first()
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    duplicate_category = db.query(models.Category).filter(
        models.Category.name == category.name,
        models.Category.user_id == current_user.id,
        models.Category.id != id
    ).first()
    if duplicate_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )

    db_category.name = category.name
    db.commit()
    db.refresh(db_category)

    return db_category

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    db_category = db.query(models.Category).filter(
        models.Category.id == id,
        models.Category.user_id == current_user.id
    ).first()
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    linked_expense = db.query(models.Expense).filter(models.Expense.category_id == id).first()
    if linked_expense:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category because it is referenced by existing expenses"
        )

    db.delete(db_category)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
