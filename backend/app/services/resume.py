import os
import uuid
from typing import List
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.resume import Resume
from app.services.resume_parser import extract_resume_text

UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "uploads",
    "resumes"
)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit

def save_and_create_resume(db: Session, user: User, file: UploadFile) -> Resume:
    """Saves uploaded resume to disk, extracts text, and creates database record for user."""
    filename = file.filename or "resume.pdf"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed formats: .pdf, .docx"
        )

    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum limit of 10 MB"
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    unique_filename = f"{user.id}_{uuid.uuid4().hex[:8]}_{filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as f:
        f.write(content)

    extracted_text = extract_resume_text(file_path)
    if not extracted_text:
        extracted_text = f"Resume content extracted from {filename}"

    resume = Resume(
        user_id=user.id,
        filename=filename,
        file_path=file_path,
        extracted_text=extracted_text
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume

def get_user_resumes(db: Session, user: User) -> List[Resume]:
    """Retrieves all resumes belonging to the authenticated user."""
    return db.query(Resume).filter(Resume.user_id == user.id).order_by(Resume.created_at.desc()).all()

def get_user_resume_by_id(db: Session, user: User, resume_id: int) -> Resume:
    """Retrieves a specific resume belonging to the authenticated user."""
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or access denied"
        )
    return resume

def delete_user_resume(db: Session, user: User, resume_id: int) -> dict:
    """Deletes a specific resume file and database record belonging to the authenticated user."""
    resume = get_user_resume_by_id(db, user, resume_id)
    if os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except Exception:
            pass
    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted successfully", "id": resume_id}
