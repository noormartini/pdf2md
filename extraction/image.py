import os
import fitz
import base64


def extract_pages_from_pdf(pdf_path: str, max_pages: int = 3) -> list[str]:
    """Render each PDF page as a base64-encoded PNG for vision LLM input."""
    doc = fitz.open(pdf_path)
    images = []

    try:
        for i, page in enumerate(doc):  # type: ignore[arg-type]
            if i >= max_pages:
                break

            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
            img_base64 = base64.b64encode(pix.tobytes("png")).decode("utf-8")
            if img_base64:
                images.append(img_base64)
    finally:
        doc.close()

    return images


def extract_embedded_images(
    pdf_path: str,
    page_idx: int,
    images_dir: str,
) -> list[str]:
    """
    Extract images embedded in a PDF page and save them to disk.

    Each image is saved as  <images_dir>/page_<N>_img_<M>.<ext>
    and a Markdown image reference is returned for each one.

    Args:
        pdf_path:   Path to the source PDF.
        page_idx:   0-based page index.
        images_dir: Directory where extracted image files will be saved.

    Returns:
        List of Markdown image references, e.g.
        ['![Figure 1, page 3](images/page_03_img_01.png)', ...]
        Empty list if the page has no embedded images.
    """
    doc = fitz.open(pdf_path)
    page = doc[page_idx]
    page_num = page_idx + 1
    md_refs = []

    try:
        image_list = page.get_images(full=True)
        if not image_list:
            return []

        os.makedirs(images_dir, exist_ok=True)

        for img_idx, img_info in enumerate(image_list, start=1):
            xref = img_info[0]
            try:
                base_image = doc.extract_image(xref)
                img_bytes = base_image["image"]
                img_ext = base_image.get("ext", "png")

                filename = f"page_{page_num:02d}_img_{img_idx:02d}.{img_ext}"
                filepath = os.path.join(images_dir, filename)

                with open(filepath, "wb") as f:
                    f.write(img_bytes)

                # Relative path so the Markdown file stays portable
                rel_path = os.path.join("images", filename).replace("\\", "/")
                md_refs.append(f"![Figure {img_idx}, page {page_num}]({rel_path})")
            except Exception:
                pass
    finally:
        doc.close()

    return md_refs
