from fastapi import APIRouter, Depends
import models
import schemas
import auth_utils

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me", response_model=schemas.UserResponse)
def get_current_user_profile(
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    return current_user

