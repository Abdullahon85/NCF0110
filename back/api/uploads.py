"""Validation of uploaded images by their actual content.

The client-supplied Content-Type and file name are ignored: the file must be a
raster image Pillow can parse in one of the allowed formats. On success the
file gets a random name with the extension of the detected format, so an
uploaded file can never be served as HTML/SVG from the backend domain.
"""
import uuid
import warnings

from PIL import Image as PILImage

ALLOWED_IMAGE_FORMATS = {"JPEG": "jpg", "PNG": "png", "GIF": "gif", "WEBP": "webp"}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_IMAGE_PIXELS = 60_000_000  # ~60 MP; guards against decompression bombs

INVALID_IMAGE_MESSAGE = "Invalid image file. Only JPEG, PNG, GIF and WebP images are allowed."


def validate_uploaded_image(file) -> tuple[bool, str | None]:
    if file.size > MAX_UPLOAD_SIZE:
        return False, f"File too large. Maximum size is {MAX_UPLOAD_SIZE // (1024 * 1024)}MB."
    try:
        file.seek(0)
        with warnings.catch_warnings():
            warnings.simplefilter("error", PILImage.DecompressionBombWarning)
            with PILImage.open(file) as img:
                width, height = img.size
                if width * height > MAX_IMAGE_PIXELS:
                    return False, "Image dimensions are too large."
                img_format = img.format
                img.verify()
    except Exception:  # Pillow raises many types for malformed/hostile input
        return False, INVALID_IMAGE_MESSAGE
    finally:
        file.seek(0)
    ext = ALLOWED_IMAGE_FORMATS.get(img_format)
    if ext is None:
        return False, INVALID_IMAGE_MESSAGE
    file.name = f"{uuid.uuid4().hex}.{ext}"
    return True, None
