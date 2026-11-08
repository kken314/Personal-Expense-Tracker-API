from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import List
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
import auth_utils

router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)

@router.get('/', response_model=List[schemas.ExpenseResponse])
def get_all_expenses(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    expenses = db.query(models.Expense).filter(models.Expense.user_id == current_user.id).all()
    return expenses

@router.get('/{id}', response_model=schemas.ExpenseResponse)
def get_expense(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    expense = db.query(models.Expense).filter(
        models.Expense.id == id,
        models.Expense.user_id == current_user.id
    ).first()
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return expense

@router.post('/', response_model=schemas.ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    category = db.query(models.Category).filter(
        models.Category.id == expense.category_id,
        models.Category.user_id == current_user.id
    ).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    new_expense = models.Expense(
        title=expense.title,
        amount=expense.amount,
        date=expense.date,
        category_id=expense.category_id,
        user_id=current_user.id
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return new_expense

@router.put('/{id}', response_model=schemas.ExpenseResponse)
def update_expense(
    id: int,
    expense: schemas.ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    db_expense = db.query(models.Expense).filter(
        models.Expense.id == id,
        models.Expense.user_id == current_user.id
    ).first()
    if not db_expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

    update_data = expense.model_dump(exclude_unset=True, exclude_none=True)

    if "category_id" in update_data:
        category = db.query(models.Category).filter(
            models.Category.id == update_data["category_id"],
            models.Category.user_id == current_user.id
        ).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    for key, value in update_data.items():
        setattr(db_expense, key, value)

    db.commit()
    db.refresh(db_expense)

    return db_expense

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    db_expense = db.query(models.Expense).filter(
        models.Expense.id == id,
        models.Expense.user_id == current_user.id
    ).first()
    if not db_expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

    db.delete(db_expense)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

