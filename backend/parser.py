import fitz  # PyMuPDF
from PIL import Image
import io
import os
import base64

def convert_pdf_to_images(file_path):
    """
    Opens a PDF and converts each page to a high-resolution PIL Image.
    We use a 2x zoom matrix to ensure the images are clear for further processing (like OCR).
    Returns a list of PIL Image objects, one for each page in the PDF.
    """
    images = []
    
    # Open the PDF document using PyMuPDF
    pdf_document = fitz.open(file_path)
    
    # Loop through each page in the document
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        # Create a matrix for 2x zoom to get high-resolution images
        zoom_matrix = fitz.Matrix(2, 2)
        
        # Convert the page to a pixel format (pixmap) using the matrix
        pix = page.get_pixmap(matrix=zoom_matrix)
        
        # Convert the PyMuPDF pixmap to a png byte stream, then open with PIL
        img_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_bytes))
        
        images.append(image)
        
    pdf_document.close()
    return images

def extract_text_from_digital_pdf(file_path):
    """
    Opens a digital PDF and extracts embedded text from every page.
    Joins the text from all pages with a newline.
    Returns the complete text as a single string.
    """
    full_text = []
    
    # Open the PDF document
    pdf_document = fitz.open(file_path)
    
    # Loop through each page and extract text
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text = page.get_text()
        full_text.append(text)
        
    pdf_document.close()
    
    # Join all the page texts together separated by a newline
    return "\n".join(full_text)

def is_digital_pdf(file_path):
    """
    Checks if a PDF is digital (text-based) or scanned (image-based).
    It inspects the first 3 pages and if the total textual characters extracted
    are more than 100, we consider it a digital PDF.
    """
    pdf_document = fitz.open(file_path)
    extracted_text_length = 0
    
    # Only check up to the first 3 pages to save time/resources
    pages_to_check = min(3, len(pdf_document))
    
    for page_num in range(pages_to_check):
        page = pdf_document.load_page(page_num)
        text = page.get_text()
        extracted_text_length += len(text.strip())
        
    pdf_document.close()
    
    # If we found more than 100 characters in the first few pages, it's a digital PDF
    if extracted_text_length > 100:
        return True
        
    # Otherwise, it's likely scanned
    return False

def pdf_to_base64_images(file_path):
    """
    Converts a PDF into a list of base64 encoded JPEG strings.
    This is useful for sending the document pages over a network API (like to an AI Vision model).
    """
    base64_images = []
    
    # Get the high-resolution PIL images using our previously defined function
    pil_images = convert_pdf_to_images(file_path)
    
    for image in pil_images:
        # Create a BytesIO buffer to hold the image data
        buffered = io.BytesIO()
        
        # JPEG doesn't support transparency/alpha channel. 
        # Convert to RGB just safely handle any RGBA/Palette images.
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
            
        # Save the PIL image to the buffer in JPEG format
        image.save(buffered, format="JPEG")
        
        # Encode the bytes from the buffer into a base64 string
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        base64_images.append(img_str)
        
    return base64_images
