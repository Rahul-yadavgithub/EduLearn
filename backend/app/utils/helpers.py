# app/utils/helpers.py

import base64
from fastapi import UploadFile


async def upload_image_as_base64(image: UploadFile) -> str:
    """
    Used for:
    - doubt image upload
    - answer image upload

    EXACT behavior preserved.
    """
    contents = await image.read()
    encoded = base64.b64encode(contents).decode("utf-8")
    content_type = image.content_type or "image/png"
    return f"data:{content_type};base64,{encoded}"


async def extract_text_from_file(file: UploadFile, limit: int = 5000) -> str:
    """
    Used for:
    - upload-reference endpoint

    Tries UTF-8 decoding, falls back to binary marker.
    """
    contents = await file.read()
    try:
        return contents.decode("utf-8")[:limit]
    except Exception:
        return f"[Binary file: {file.filename}]"
