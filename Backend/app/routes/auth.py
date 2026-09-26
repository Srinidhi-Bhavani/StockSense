from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest
)
from app.schemas.user import UserResponse
from app.services.auth_service import (
    signup,
    login,
    logout,
    generate_otp,
    reset_password
)
from app.utils.auth import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# -------------------------
# SIGNUP
# -------------------------
@router.post("/signup", response_model=UserResponse)
def signup_route(
    data: SignupRequest,
    db: Session = Depends(get_db)
):
    user = signup(
        db,
        data.name,
        data.email,
        data.password
    )
    return user


# -------------------------
# LOGIN
# -------------------------
@router.post("/login")
def login_route(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    token = login(
        db,
        data.email,
        data.password
    )

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer"
    }


# -------------------------
# CURRENT USER PROFILE
# -------------------------
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# -------------------------
# LOGOUT
# -------------------------
@router.post("/logout")
def logout_route(
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    token = authorization.replace("Bearer ", "").strip()
    logout(token)
    return {
        "message": "Successfully logged out"
    }


# -------------------------
# FORGOT PASSWORD
# -------------------------
@router.post("/forgot-password")
def forgot_password_route(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    otp = generate_otp(
        db,
        data.email
    )

    return {
        "message": "OTP generated successfully",
        "otp": otp
    }


# -------------------------
# RESET PASSWORD
# -------------------------
@router.post("/reset-password")
def reset_password_route(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    reset_password(
        db,
        data.email,
        data.otp,
        data.new_password
    )

    return {
        "message": "Password reset successful"
    }