import random
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt

from app.models.user import User


# Password hashing
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

# JWT settings
SECRET_KEY = "stocksense-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# In-memory OTP storage: email -> {"otp": str, "expires_at": datetime}
otp_storage = {}

# In-memory token blacklist for logout
revoked_tokens = set()


# -------------------------
# SIGNUP
# -------------------------
def signup(
    db: Session,
    name: str,
    email: str,
    password: str,
    role: str = "staff"
):
    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = pwd_context.hash(password)

    user = User(
        name=name,
        email=email,
        password=hashed_password,
        role=role,
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# -------------------------
# LOGIN
# -------------------------
def login(
    db: Session,
    email: str,
    password: str
):
    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not pwd_context.verify(password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User account is inactive"
        )

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode(
        {
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
            "exp": expire
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# -------------------------
# LOGOUT
# -------------------------
def logout(token: str):
    revoked_tokens.add(token)
    return True


def is_token_revoked(token: str) -> bool:
    return token in revoked_tokens


# -------------------------
# FORGOT PASSWORD / OTP
# -------------------------
def generate_otp(
    db: Session,
    email: str
):
    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User with this email does not exist"
        )

    otp = str(random.randint(100000, 999999))
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    otp_storage[email] = {
        "otp": otp,
        "expires_at": expires_at
    }

    return otp


# -------------------------
# RESET PASSWORD
# -------------------------
def reset_password(
    db: Session,
    email: str,
    otp: str,
    new_password: str
):
    record = otp_storage.get(email)

    if not record:
        raise HTTPException(
            status_code=400,
            detail="OTP not found or expired"
        )

    if datetime.utcnow() > record["expires_at"]:
        del otp_storage[email]
        raise HTTPException(
            status_code=400,
            detail="OTP has expired. Please request a new one."
        )

    if record["otp"] != otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.password = pwd_context.hash(new_password)
    db.commit()

    # Remove OTP after successful reset
    del otp_storage[email]

    return True