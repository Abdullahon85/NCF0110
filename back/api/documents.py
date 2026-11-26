"""Product documents (passport, manual, firmware...): PDF, Word, Excel and archives only.

The type is checked by the first bytes of the file, not by the name the browser sent, and the
file is saved under a random name with the detected extension, so an uploaded document can
never be served as a web page from the site's own domain.
"""

import uuid

MAX_DOCUMENT_SIZE = 20 * 1024 * 1024  # 20 MB

_ZIP = b"PK\x03\x04"
_OLE = bytes.fromhex("D0CF11E0A1B11AE1")  # old Word / Excel
SIGNATURES = {
    "pdf": b"%PDF",
    "docx": _ZIP,
    "xlsx": _ZIP,
    "zip": _ZIP,
    "doc": _OLE,
    "xls": _OLE,
    "rar": b"Rar!\x1a\x07",
}

INVALID_DOCUMENT_MESSAGE = "Можно загрузить PDF, DOC, DOCX, XLS, XLSX, ZIP или RAR до 20 МБ."


def validate_uploaded_document(file) -> tuple[bool, str | None]:
    if file.size > MAX_DOCUMENT_SIZE:
        return False, INVALID_DOCUMENT_MESSAGE
    ext = file.name.rsplit(".", 1)[-1].lower() if "." in file.name else ""
    signature = SIGNATURES.get(ext)
    if signature is None:
        return False, INVALID_DOCUMENT_MESSAGE
    file.seek(0)
    head = file.read(len(signature))
    file.seek(0)
    if head != signature:
        return False, INVALID_DOCUMENT_MESSAGE
    file.name = f"{uuid.uuid4().hex}.{ext}"
    return True, None
