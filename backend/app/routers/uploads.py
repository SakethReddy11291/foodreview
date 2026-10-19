import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.config import settings
from app.core.deps import get_current_user
from app.models import User
from app.services.images import looks_like_image

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_BYTES = 5 * 1024 * 1024  # 5 MB


@router.post("/photo")
def upload_photo(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    if not (
        settings.cloudinary_cloud_name
        and settings.cloudinary_api_key
        and settings.cloudinary_api_secret
    ):
        raise HTTPException(status_code=503, detail="Photo uploads are not configured")
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Only JPEG, PNG or WEBP images are allowed")

    data = file.file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Image must be 5 MB or smaller")
    if not looks_like_image(data):
        raise HTTPException(status_code=400, detail="File is not a valid image")

    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )
    try:
        result = cloudinary.uploader.upload(
            data,
            folder="foodreview/reviews",
            resource_type="image",
            transformation=[{"width": 1280, "height": 1280, "crop": "limit"}, {"quality": "auto"}],
        )
    except Exception:
        raise HTTPException(status_code=502, detail="Photo upload failed, please try again")
    return {"url": result["secure_url"]}
