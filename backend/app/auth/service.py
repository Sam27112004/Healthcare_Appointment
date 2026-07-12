from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User, Patient
from app.auth.schemas import PatientRegisterRequest, LoginRequest
from app.auth.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.schemas.enums import Role

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_patient(self, request: PatientRegisterRequest) -> User:
        # Check if email exists
        stmt = select(User).where(User.email == request.email)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        # Validate password strength (simple check)
        if not any(char.isdigit() for char in request.password) or not any(char.isupper() for char in request.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least 1 uppercase letter and 1 digit")

        # Create user
        user = User(
            email=request.email,
            hashed_password=get_password_hash(request.password),
            full_name=request.full_name,
            phone=request.phone,
            role=Role.PATIENT.value
        )
        self.db.add(user)
        await self.db.flush() # flush to get user.id

        # Create patient profile
        patient = Patient(
            user_id=user.id,
            date_of_birth=request.date_of_birth,
            gender=request.gender,
            blood_group=request.blood_group,
            address=request.address,
            medical_history=request.medical_history
        )
        self.db.add(patient)
        
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def authenticate_user(self, request: LoginRequest) -> User:
        stmt = select(User).where(User.email == request.email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(request.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
            
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")
            
        return user
