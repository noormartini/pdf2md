import base64
import os

import fitz


def extract_page_figures(
    page: fitz.Page,
    doc: fitz.Document,
    page_num: int,
    figures_dir: str,
) -> list[str]:
    """Extract embedded images from a PDF page and save them as files.

    Returns relative paths (`figures/<filename>`) suitable for Markdown image links.
    Images are saved under `figures_dir`; the returned paths assume the Markdown
    file lives in the parent directory of `figures_dir`.
    """
    os.makedirs(figures_dir, exist_ok=True)
    refs: list[str] = []

    for fig_idx, img_info in enumerate(page.get_images(full=True), start=1):
        xref = img_info[0]
        try:
            img_dict = doc.extract_image(xref)
        except Exception:
            continue

        ext = img_dict.get("ext", "png")
        img_bytes = img_dict["image"]
        filename = f"page_{page_num + 1:03d}_fig_{fig_idx:03d}.{ext}"
        filepath = os.path.join(figures_dir, filename)

        with open(filepath, "wb") as f:
            f.write(img_bytes)

        refs.append(f"figures/{filename}")

    return refs


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
