import os
from typing import Dict, Any, Optional
import firebase_admin
from firebase_admin import credentials, auth
from app.core.config import settings

def get_firebase_app():
    """Initializes Firebase Admin SDK if not already initialized."""
    if not firebase_admin._apps:
        cred_path = settings.FIREBASE_CREDENTIALS_PATH
        resolved_path = None
        if cred_path:
            if os.path.exists(cred_path):
                resolved_path = cred_path
            else:
                # Check relative to project root (parent of backend directory)
                from app.core.config import BASE_DIR
                project_root = os.path.dirname(BASE_DIR)
                candidate = os.path.join(project_root, cred_path)
                if os.path.exists(candidate):
                    resolved_path = candidate

        if resolved_path:
            cred = credentials.Certificate(resolved_path)
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
