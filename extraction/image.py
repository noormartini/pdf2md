import base64
import os

import fitz

from extraction.text import _MONOSPACE_FONT_MARKERS


def _bbox_is_code_listing(page: fitz.Page, bbox: fitz.Rect, threshold: float = 0.3) -> bool:
    """Return True if a bounding box's text is dominated by a monospace font.

    LaTeX's `listings` package draws a shaded box (a vector-filled rectangle)
    behind source-code listings — that vector content is decorative styling
    around text, not a diagram, and must not be mistaken for one.
    """
    d = page.get_text("dict", clip=bbox)
    total = 0
    mono = 0
    for block in d["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                n = len(span["text"])
                total += n
                if any(m in span["font"].lower() for m in _MONOSPACE_FONT_MARKERS):
                    mono += n
    return total > 0 and (mono / total) >= threshold


def _vector_drawing_bbox(page: fitz.Page) -> fitz.Rect | None:
    """Return the bounding box covering all of a page's vector drawings.

    Covers charts/plots exported as vector paths (e.g. matplotlib figures
    embedded in the PDF) — these have no XObject image for get_images() to
    find. Returns None for boxes that are too small to be a real figure, or
    that turn out to be a decorative box around a source-code listing.
    """
    drawings = page.get_drawings()
    rects = [d["rect"] for d in drawings if d.get("rect")]
    if not rects:
        return None

    bbox = rects[0]
    for r in rects[1:]:
        bbox.include_rect(r)

    # Skip vanishingly small bounding boxes — stray marks, not real figures.
    if bbox.width < 50 or bbox.height < 50:
        return None

    if _bbox_is_code_listing(page, bbox):
        return None

    return bbox


def _render_region(page: fitz.Page, bbox: fitz.Rect, dpi: int = 200) -> bytes:
    """Rasterise a page region (as actually composited — raster + vector) to PNG."""
    matrix = fitz.Matrix(dpi / 72, dpi / 72)
    pixmap = page.get_pixmap(matrix=matrix, clip=bbox)
    return pixmap.tobytes("png")


def _is_blank_raster(img_bytes: bytes, threshold: float = 0.9) -> bool:
    """Return True if a single color covers most of the image (a blank frame/background)."""
    try:
        pixmap = fitz.Pixmap(img_bytes)
    except Exception:
        return False
    usage, _ = pixmap.color_topusage()
    return usage >= threshold


def _overlapping_raster_xrefs(page: fitz.Page, doc: fitz.Document, raster_images: list, vector_bbox: fitz.Rect) -> tuple[set[int], bool]:
    """Split rasters into those overlapping the vector bbox vs. unrelated ones.

    Diagrams like activity charts are often composed of a small decorative
    raster (a background frame or divider strip) plus the real content drawn
    as vector paths on top. Returns the xrefs of rasters that overlap the
    vector content (these should not be extracted individually — they're
    either the decorative background or a legend/colorbar strip that the
    vector-region render will already capture), and whether a "dominant"
    raster was found among them (one that covers most of the vector bbox and
    isn't itself a near-blank placeholder — if found, the raster is the real
    figure and the vector bbox should NOT be rendered separately).
    """
    vector_area = vector_bbox.width * vector_bbox.height
    overlapping_xrefs: set[int] = set()
    dominant_found = False

    for img_info in raster_images:
        xref = img_info[0]
        for rect in page.get_image_rects(xref):
            overlap = rect & vector_bbox
            if overlap.is_empty:
                continue
            overlapping_xrefs.add(xref)
            if overlap.width * overlap.height < 0.6 * vector_area:
                continue
            try:
                img_bytes = doc.extract_image(xref)["image"]
            except Exception:
                continue
            if not _is_blank_raster(img_bytes):
                dominant_found = True

    return overlapping_xrefs, dominant_found


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

    Falls back to cropping the page's vector-drawing bounding box when there
    are no embedded raster images, or when the embedded raster is clearly
    just a decorative background/frame and the actual figure (e.g. an
    activity diagram or matplotlib chart) is drawn as vector paths on top of
    it — extracting the raw raster bytes in that case would save a blank
    frame instead of the figure.
    """
    os.makedirs(figures_dir, exist_ok=True)
    refs: list[str] = []
    fig_idx = 1

    raster_images = page.get_images(full=True)
    vector_bbox = _vector_drawing_bbox(page)

    overlapping_xrefs: set[int] = set()
    if vector_bbox is not None and raster_images:
        overlapping_xrefs, dominant_found = _overlapping_raster_xrefs(page, doc, raster_images, vector_bbox)
    else:
        dominant_found = False

    if vector_bbox is not None and not dominant_found:
        # Include any raster images overlapping the vector content (e.g. a
        # heatmap's colorbar legend exported as a raster strip) so the
        # render still captures them alongside the vector-drawn figure body.
        # Rasters elsewhere on the page (unrelated screenshots) are left for
        # the normal extraction loop below.
        combined_bbox = fitz.Rect(vector_bbox)
        for img_info in raster_images:
            if img_info[0] not in overlapping_xrefs:
                continue
            for rect in page.get_image_rects(img_info[0]):
                combined_bbox.include_rect(rect)

        cropped = _render_region(page, combined_bbox)
        filename = f"page_{page_num + 1:03d}_fig_{fig_idx:03d}.png"
        filepath = os.path.join(figures_dir, filename)
        with open(filepath, "wb") as f:
            f.write(cropped)
        refs.append(f"figures/{filename}")
        fig_idx += 1
    else:
        # The dominant raster already represents the vector content; don't
        # skip extracting it below.
        overlapping_xrefs = set()

    for img_info in raster_images:
        xref = img_info[0]
        if xref in overlapping_xrefs:
            continue  # already captured by the vector-region render above

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
        fig_idx += 1

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
