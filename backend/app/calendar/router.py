import json
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from google_auth_oauthlib.flow import Flow
from app.auth.dependencies import get_current_user, get_db
from app.models.user import User
from app.config import settings

router = APIRouter(prefix="/calendar", tags=["Calendar Integration"])

# Define the scopes required by your application
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_client_config():
    # Construct client config dynamically from env
    return {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "project_id": "healthcare-app",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
        }
    }

@router.get("/auth")
async def initiate_google_oauth(current_user: User = Depends(get_current_user)):
    """Initiate the Google OAuth 2.0 flow"""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google Client ID/Secret not configured")
        
    flow = Flow.from_client_config(
        get_client_config(),
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent' # Force consent to get refresh token
    )
    
    # We pass the user_id in the state so we can link the tokens back to them in the callback
    state_payload = {"user_id": str(current_user.id), "oauth_state": state}
    state_encoded = json.dumps(state_payload)
    
    # We rebuild the url with our custom state
    flow = Flow.from_client_config(
        get_client_config(),
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
        state=state_encoded
    )
    authorization_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    return RedirectResponse(authorization_url)

@router.get("/callback")
async def google_oauth_callback(request: Request, state: str, code: str, db: AsyncSession = Depends(get_db)):
    """Handle Google OAuth callback and save tokens to User table"""
    try:
        state_payload = json.loads(state)
        user_id = state_payload.get("user_id")
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID missing in state")

    flow = Flow.from_client_config(
        get_client_config(),
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
        state=state
    )
    
    # URL that Google redirected to
    authorization_response = str(request.url)
    
    try:
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"OAuth failure: {e}")

    # Save to database
    stmt = select(User).where(User.id == user_id)
    user = (await db.execute(stmt)).scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    user.google_access_token = credentials.token
    if credentials.refresh_token:
        user.google_refresh_token = credentials.refresh_token
        
    await db.commit()
    
    return {"message": "Google Calendar successfully connected"}
