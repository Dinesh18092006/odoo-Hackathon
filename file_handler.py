"""File upload handler — validates and saves files to local storage."""
import os
import uuid
import shutil
from fastapi import UploadFile
from config import settings
from utils.exceptions import FileTooLargeException, InvalidFileTypeException
from utils.constants import (
    ALLOWED_IMAGE_MIME_TYPES,
    ALLOWED_DOCUMENT_MIME_TYPES,
    MAX_FILE_SIZE_BYTES,
)


def _ensure_dir(path: str) -> None:
    """Create directory if it does not exist."""
    os.makedirs(path, exist_ok=True)


async def save_asset_image(file: UploadFile, asset_id: str) -> dict:
    """
    Validate and save an asset image upload.
    Returns dict with file metadata.
    """
    if file.content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise InvalidFileTypeException("JPEG, PNG, WebP, GIF")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise FileTooLargeException(settings.max_file_size_mb)

    save_dir = os.path.join(settings.upload_dir, "assets", "images", asset_id)
    _ensure_dir(save_dir)

    ext = os.path.splitext(file.filename or "image.jpg")[1] or ".jpg"
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(save_dir, unique_name)

    with open(file_path, "wb") as f:
        f.write(contents)

    return {
        "file_name": file.filename or unique_name,
        "file_path": file_path,
        "file_size": len(contents),
        "mime_type": file.content_type,
        "relative_url": f"/uploads/assets/images/{asset_id}/{unique_name}",
    }


async def save_asset_document(file: UploadFile, asset_id: str) -> dict:
    """
    Validate and save an asset document upload.
    Returns dict with file metadata.
    """
    if file.content_type not in ALLOWED_DOCUMENT_MIME_TYPES:
        raise InvalidFileTypeException("PDF")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise FileTooLargeException(settings.max_file_size_mb)

    save_dir = os.path.join(settings.upload_dir, "assets", "documents", asset_id)
    _ensure_dir(save_dir)

    unique_name = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join(save_dir, unique_name)

    with open(file_path, "wb") as f:
        f.write(contents)

    return {
        "file_name": file.filename or unique_name,
        "file_path": file_path,
        "file_size": len(contents),
        "mime_type": file.content_type,
        "relative_url": f"/uploads/assets/documents/{asset_id}/{unique_name}",
    }


def delete_file(file_path: str) -> None:
    """Safely delete a file if it exists."""
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
