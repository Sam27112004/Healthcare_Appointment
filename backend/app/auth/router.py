from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.schemas import PatientRegisterRequest, LoginRequest, TokenResponse, RefreshRequest, UserResponse
from app.auth.service import AuthService
from app.auth.dependencies import get_db, get_current_user
from app.auth.security import create_access_token, create_refresh_token
from app.models.user import User
import jwt
from jwt.exceptions import InvalidTokenError
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: PatientRegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new patient account."""
    service = AuthService(db)
    user = await service.register_patient(request)
    
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate any user (patient, doctor, admin)."""
    service = AuthService(db)
    user = await service.authenticate_user(request)
    
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )

@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Refresh an expired access token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(request.refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id_str: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")
        if user_id_str is None or token_type != "refresh":
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
        
    access_token = create_access_token(subject=user_id_str)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=request.refresh_token # Optionally issue a new refresh token, returning old for now
    )

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: User = Depends(get_current_user)):
    """Invalidate the current refresh token. For stateless JWTs, this is often handled client-side by deleting tokens."""
    # In a full implementation, you could add the token to a Redis blacklist here
    return {"message": "Successfully logged out"}
