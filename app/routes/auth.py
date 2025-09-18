from fastapi import APIRouter, status, Depends, HTTPException, BackgroundTasks, Request
from app.config import database, api
from app.schemas.auth import Token
from app.models import UserModel, UserVerificationToken
from sqlalchemy.orm import Session
import app.utils.auth as auth_utility
import app.utils.email as email_utility
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth import UserRegistrationRequest
from app.schemas.auth import UserRegistrationResponse
from app.schemas.auth import RefreshTokenRequest, ForgotPasswordRequest, ResetPasswordRequest
from datetime import datetime, timezone


router = APIRouter(prefix="/auth", tags=["Auth"])


# Endpoint for user registration
@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserRegistrationResponse)
def register(payload: UserRegistrationRequest, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(database.get_db)):
    payload.password = auth_utility.hash_password(payload.password)
    data = payload.model_dump()
    user = UserModel(**data)
    db.add(user)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    db.refresh(user)
    v_token = auth_utility.create_user_verification_token(
        user_id=user.id, type="new_signup", size=64, validity=24, db=db)
    email_utility.send_signup_verification_email(user.email, v_token, background_tasks, request)
    return user

# Endpoint for user login


@router.post('/login', response_model=Token)
def login(creds: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    print(db)
    user = db.query(UserModel).filter(UserModel.email == creds.username).first()

    if not user or not auth_utility.verify_password(creds.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect login credentials", headers={"WWW-Authenticate": "Bearer"})
    elif not user.is_verified and api.force_email_verification:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Email not verified. Please verify your email before logging in.")
    else:
        access_token = auth_utility.create_access_token(data={"user_id": str(user.id)})
        refresh_token, refresh_expiry = auth_utility.create_refresh_token(data={"user_id": str(user.id)})
        # Store refresh token and expiry in DB
        user.refresh_token = refresh_token
        user.refresh_token_expiry = refresh_expiry
        user.last_login = datetime.now(timezone.utc)
        db.add(user)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed.")
        db.refresh(user)
        return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


# Endpoint to refresh access token
@router.post('/refresh', response_model=Token)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(database.get_db)):
    # Find user by refresh token
    user = db.query(UserModel).filter(UserModel.refresh_token == payload.refresh_token).first()
    if not user or not user.refresh_token or not user.refresh_token_expiry:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    # Check expiry
    if user.refresh_token_expiry < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    # Verify token
    user_id = auth_utility.verify_refresh_token(payload.refresh_token)
    if str(user.id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    # Issue new tokens
    access_token = auth_utility.create_access_token(data={"user_id": str(user.id)})
    new_refresh_token, new_refresh_expiry = auth_utility.create_refresh_token(data={"user_id": str(user.id)})
    user.refresh_token = new_refresh_token
    user.refresh_token_expiry = new_refresh_expiry
    db.add(user)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not refresh access token.")
    db.refresh(user)
    return Token(access_token=access_token, refresh_token=new_refresh_token, token_type="bearer")


# Endpoint to verify email
@router.get('/verify', status_code=status.HTTP_200_OK)
def verify_email(db: Session = Depends(database.get_db), token: str = None):
    token = db.query(UserVerificationToken).filter(UserVerificationToken.token ==
                                                   token, UserVerificationToken.type == 'new_signup').first()
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token")
    if token.is_verified:
        return {"message": "Email already verified."}
    if not token.token_expiry or token.token_expiry < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token has expired")
    token.is_verified = True
    token.token = None
    token.updated_at = datetime.now(timezone.utc)
    db.add(token)
    user = db.query(UserModel).filter(UserModel.id == token.user_id).first()
    user.is_verified = True
    db.add(user)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Email verification failed.")
    return {"message": "Email verified successfully."}


# Endpoint for user logout
# invalidate the user's refresh token in the database, so it cannot be used to obtain new access tokens.
@router.post('/logout', status_code=200)
def logout(db: Session = Depends(database.get_db), current_user: UserModel = Depends(auth_utility.get_current_user)):
    current_user.refresh_token = None
    current_user.refresh_token_expiry = None
    db.add(current_user)
    db.commit()
    return {"message": "Logged out successfully."}


@router.post('/forget-password', status_code=status.HTTP_200_OK)
def forget_password(payload: ForgotPasswordRequest, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(database.get_db)):
    user = db.query(UserModel).filter(UserModel.email == payload.email).first()
    if user:
        v_token = auth_utility.create_user_verification_token(
            user_id=user.id, type="password_reset", size=64, validity=1, db=db)
        email_utility.send_password_reset_verification_email(user.email, v_token, background_tasks, request)
        return {
            "message": f"A link has been sent to the email id."
        }
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with email {user.email} does not exist.")


@router.post('/reset-password')
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(database.get_db)):
    token = db.query(UserVerificationToken).filter(
        UserVerificationToken.token == payload.token,
        UserVerificationToken.type == 'password_reset',
        UserVerificationToken.is_verified == False,
        UserVerificationToken.token_expiry > datetime.now(timezone.utc)
    ).first()
    if token:
        user = db.query(UserModel).filter(UserModel.id == token.user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User not found")
        else:
            user.password = auth_utility.hash_password(payload.new_password)
            token.is_verified = True
            token.token = None
            token.updated_at = datetime.now(timezone.utc)
            db.add(user)
            db.add(token)
            try:
                db.commit()
                return {
                    "message": "Password reset done successfully."
                }
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_200_OK, detail=f"Failed to reset password.")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid token.")
