from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserProfileResponse, UserProfileUpdateRequest, UpdatePasswordRequest, UserProfileCreateRequest, UpdatePasswordResponse
from app.utils import auth as auth_util
from app.models import User, UserProfile
from sqlalchemy.orm import Session
from app.config import database


router = APIRouter(prefix="/user", tags=["User"])


@router.get("/profile", response_model=UserProfileResponse, status_code=status.HTTP_200_OK)
def get_user(current_user: User = Depends(auth_util.get_current_user)):
    profile = current_user.profile
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_verified": current_user.is_verified,
        "full_name": profile.full_name if profile else None,
        "country": profile.country if profile else None,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "notifications": current_user.notifications
    }


@router.post('/profile')
def create_user_profile(payload: UserProfileCreateRequest, current_user: User = Depends(auth_util.get_current_user), db: Session = Depends(database.get_db)):
    user_profile = UserProfile(user_id=current_user.id, full_name=payload.full_name, country=payload.country)
    db.add(user_profile)

    try:
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create user profile.")

    db.refresh(user_profile)
    return user_profile


@router.put("/profile")
def update_user_profile(payload: UserProfileUpdateRequest, current_user: User = Depends(auth_util.get_current_user), db: Session = Depends(database.get_db)):
    current_user.profile.full_name = payload.full_name
    current_user.profile.country = payload.country
    user_profile = current_user.profile
    db.add(user_profile)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update user profile.")

    db.refresh(user_profile)
    return user_profile


@router.put('/update-password', status_code=status.HTTP_200_OK)
def update_password(payload: UpdatePasswordRequest, current_user: User = Depends(auth_util.get_current_user), db: Session = Depends(database.get_db)):
    if auth_util.verify_password(payload.old_password, current_user.password):
        current_user.password = auth_util.hash_password(payload.new_password)
        db.add(current_user)

        try:
            db.commit()
            return UpdatePasswordResponse(message="Password updated successfully")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to update password.")

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to update user password.")
