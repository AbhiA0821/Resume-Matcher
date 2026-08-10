import os
from typing import Dict, Any, Optional
import firebase_admin
from firebase_admin import credentials, auth
from app.core.config import settings

def get_firebase_app():
    """Initializes Firebase Admin SDK if not already initialized."""
    if not firebase_admin._apps:
        cred_path = settings.FIREBASE_CREDENTIALS_PATH
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            try:
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred)
            except Exception:
                # Initialize default app shell for verification attempts
                firebase_admin.initialize_app()
    return firebase_admin.get_app()

def verify_firebase_id_token(id_token: str) -> Dict[str, Any]:
    """Verifies Firebase ID token using Firebase Admin SDK.
    Returns decoded token claims dictionary or raises Exception if invalid/unconfigured."""
    get_firebase_app()
    decoded_token = auth.verify_id_token(id_token)
    return decoded_token
