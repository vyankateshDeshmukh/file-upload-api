from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os
from datetime import datetime
import uuid
import time

load_dotenv()

router = APIRouter()

# Cloudinary Config
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

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


# Background Task Function
def process_file(filename: str):
    print(f"Processing started for: {filename}")
    time.sleep(5)
    print(f"Processing completed for: {filename}")


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

    # Upload to Cloudinary
    upload_result = cloudinary.uploader.upload(
        file_bytes,
        resource_type="auto"
    )

    # Generate metadata
    file_id = str(uuid.uuid4())

    # Start background processing
    background_tasks.add_task(process_file, file.filename)

    return {
        "file_id": file_id,
        "filename": file.filename,
        "file_size_bytes": len(file_bytes),
        "file_type": file.content_type,
        "uploaded_at": str(datetime.now()),
        "url": upload_result["secure_url"],
        "message": "File uploaded successfully ✅",
        "background_task": "Processing started"
    }