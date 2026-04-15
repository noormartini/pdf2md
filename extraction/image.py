import fitz
import base64
from io import BytesIO


def extract_pages_from_pdf(pdf_path: str, max_pages: int = 3) -> list[str]:
    """Extract images page by page from the PDF as base64-encoded strings."""
    doc = fitz.open(pdf_path)
    images = []

    try:
        for i, page in enumerate(doc):  # type: ignore[arg-type]
            if i >= max_pages:
                break

            # Get page as image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
            img_data = pix.tobytes("png")
            
            # Encode to base64
            img_base64 = base64.b64encode(img_data).decode("utf-8")
            if img_base64:
                images.append(img_base64)
    finally:
        doc.close()

    return images
