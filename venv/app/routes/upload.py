from fastapi import APIRouter, UploadFile, File, HTTPException
import cloudinary
import cloudinary.uploader
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)

# Allowed file types
ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "pdf"]

# Max file size = 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    # Get file extension
    extension = file.filename.split(".")[-1].lower()

    # Validate file type
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type"
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 5MB"
        )

    try:
        # Generate unique file ID
        file_id = str(uuid.uuid4())

        # File metadata
        file_size = len(content)
        file_type = file.content_type
        uploaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Upload file to Cloudinary
        result = cloudinary.uploader.upload(
            content,
            resource_type="auto",
            folder="file_upload_api"
        )

        return {
            "file_id": file_id,
            "filename": file.filename,
            "file_size_bytes": file_size,
            "file_type": file_type,
            "uploaded_at": uploaded_at,
            "url": result["secure_url"],
            "message": "File uploaded successfully ✅"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )