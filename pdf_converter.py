import os
import pdfplumber
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image
import io


def _set_font(run, is_code=False):
    """
    Set appropriate fonts for text to ensure compatibility with Microsoft Word.
    """
    if is_code:
        run.font.name = 'Consolas'
        run.font.size = Pt(9)
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    else:
        run.font.name = 'Calibri'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
        run._element.rPr.rFonts.set(qn('w:ascii'), 'Calibri')
        run._element.rPr.rFonts.set(qn('w:hAnsi'), 'Calibri')


def convert_pdf_to_docx(pdf_file_path, output_path, extract_images=True):
    """
    Convert a PDF file to a Word document.

    Args:
        pdf_file_path: Path to the PDF file
        output_path: Path where the Word document should be saved
        extract_images: Whether to extract and embed images from PDF
    """
    # Create Word document
    doc = Document()

    # Open PDF file
    with pdfplumber.open(pdf_file_path) as pdf:
        print(f"[DEBUG] Processing PDF with {len(pdf.pages)} pages")

        for page_num, page in enumerate(pdf.pages, 1):
            print(f"[DEBUG] Processing page {page_num}/{len(pdf.pages)}")

            # Add page number heading (except for first page)
            if page_num > 1:
                doc.add_page_break()
                page_heading = doc.add_heading(f'Page {page_num}', level=2)
                for run in page_heading.runs:
                    _set_font(run)

            # Extract text from page
            text = page.extract_text()
            if text:
                # Split text into paragraphs
                paragraphs = text.split('\n')
                for para_text in paragraphs:
                    if para_text.strip():
                        # Detect if it looks like a heading (all caps, short, etc.)
                        if _is_heading(para_text):
                            heading = doc.add_heading(para_text.strip(), level=3)
                            for run in heading.runs:
                                _set_font(run)
                        else:
                            p = doc.add_paragraph(para_text.strip())
                            for run in p.runs:
                                _set_font(run)

            # Extract tables
            tables = page.extract_tables()
            if tables:
                print(f"[DEBUG] Found {len(tables)} tables on page {page_num}")
                for table_data in tables:
                    _add_table_to_doc(doc, table_data)

            # Extract images if requested
            if extract_images:
                try:
                    # Get images from page
                    images = page.images
                    if images:
                        print(f"[DEBUG] Found {len(images)} images on page {page_num}")
                        for img_index, img in enumerate(images):
                            try:
                                _extract_and_add_image(doc, page, img, page_num, img_index)
                            except Exception as e:
                                print(f"[DEBUG] Error extracting image {img_index} from page {page_num}: {e}")
                except Exception as e:
                    print(f"[DEBUG] Error processing images on page {page_num}: {e}")

    # Save document
    doc.save(output_path)
    print(f"[DEBUG] PDF converted successfully to {output_path}")


def _is_heading(text):
    """
    Detect if text looks like a heading.
    """
    text = text.strip()
    # Check if text is short and mostly uppercase
    if len(text) < 100 and text.isupper():
        return True
    # Check if text starts with numbers (like "1. ", "1.1 ")
    if text and text[0].isdigit() and ('.' in text[:10] or ')' in text[:10]):
        return True
    return False


def _add_table_to_doc(doc, table_data):
    """
    Add a table to the Word document.
    """
    if not table_data or len(table_data) == 0:
        return

    # Filter out None rows and get dimensions
    valid_rows = [row for row in table_data if row and any(cell for cell in row)]
    if not valid_rows:
        return

    num_rows = len(valid_rows)
    num_cols = max(len(row) for row in valid_rows)

    # Create Word table
    table = doc.add_table(rows=num_rows, cols=num_cols)
    table.style = 'Light Grid Accent 1'

    # Fill table
    for i, row in enumerate(valid_rows):
        for j, cell in enumerate(row):
            if j < num_cols and cell is not None:
                table.rows[i].cells[j].text = str(cell).strip()
                # Set font for table cells
                for paragraph in table.rows[i].cells[j].paragraphs:
                    for run in paragraph.runs:
                        _set_font(run)
                # Make first row bold (header)
                if i == 0:
                    for paragraph in table.rows[i].cells[j].paragraphs:
                        for run in paragraph.runs:
                            run.bold = True

    # Add spacing after table
    doc.add_paragraph()


def _extract_and_add_image(doc, page, img_info, page_num, img_index):
    """
    Extract image from PDF page and add to Word document.
    """
    try:
        # Get image coordinates
        x0, y0, x1, y1 = img_info['x0'], img_info['top'], img_info['x1'], img_info['bottom']

        # Crop image from page
        bbox = (x0, y0, x1, y1)
        cropped_page = page.crop(bbox)

        # Convert to image
        img = cropped_page.to_image(resolution=150)

        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        # Add to document
        # Calculate width (max 6 inches)
        width = min(6, (x1 - x0) / 72)  # Convert points to inches
        doc.add_picture(img_bytes, width=Inches(width))
        doc.add_paragraph()  # Add spacing after image

        print(f"[DEBUG] Added image {img_index} from page {page_num}")
    except Exception as e:
        print(f"[DEBUG] Could not extract image {img_index} from page {page_num}: {e}")
        # Add placeholder text
        p = doc.add_paragraph(f'[Image {img_index} from page {page_num}]')
        for run in p.runs:
            run.italic = True
            _set_font(run)


def convert_pdf_to_docx_simple(pdf_file_path, output_path):
    """
    Simple PDF to Word conversion (text only, no images).
    Faster and more reliable for text-heavy PDFs.
    """
    doc = Document()

    with pdfplumber.open(pdf_file_path) as pdf:
        print(f"[DEBUG] Processing PDF with {len(pdf.pages)} pages (simple mode)")

        for page_num, page in enumerate(pdf.pages, 1):
            # Add page break (except for first page)
            if page_num > 1:
                doc.add_page_break()

            # Extract text
            text = page.extract_text()
            if text:
                paragraphs = text.split('\n')
                for para_text in paragraphs:
                    if para_text.strip():
                        if _is_heading(para_text):
                            heading = doc.add_heading(para_text.strip(), level=3)
                            for run in heading.runs:
                                _set_font(run)
                        else:
                            p = doc.add_paragraph(para_text.strip())
                            for run in p.runs:
                                _set_font(run)

            # Extract tables
            tables = page.extract_tables()
            if tables:
                for table_data in tables:
                    _add_table_to_doc(doc, table_data)

    doc.save(output_path)
    print(f"[DEBUG] PDF converted successfully (simple mode)")
