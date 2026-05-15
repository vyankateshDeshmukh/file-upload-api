from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime
import time
import re

load_dotenv()

router = APIRouter()

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)

# Allowed file types
ALLOWED_TYPES = [
    "image/jpeg",
    "image/png",
    "application/pdf"
]

# Max file size = 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024


# Background task
def process_file(filename: str):
    print(f"Processing started for: {filename}")
    time.sleep(3)
    print(f"Processing completed for: {filename}")


# Secure filename
def secure_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)


@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):

    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG, and PDF files are allowed"
        )

    # Read file
    file_bytes = await file.read()

    # Validate file size
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 5MB limit"
        )

    # Secure filename
    safe_filename = secure_filename(file.filename)

    try:

        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            file_bytes,
            public_id=safe_filename,
            resource_type="auto",
            folder="file_upload_api"
        )

        # Generate metadata
        file_id = str(uuid.uuid4())

        # Start background task
        background_tasks.add_task(process_file, safe_filename)

        return {
            "status": "success",
            "file_id": file_id,
            "filename": safe_filename,
            "file_size_bytes": len(file_bytes),
            "file_type": file.content_type,
            "uploaded_at": str(datetime.now()),
            "url": upload_result["secure_url"],
            "message": "Secure file upload successful ✅"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
