import os
import json
import base64
import google.generativeai as genai
from dotenv import load_dotenv

# Import our custom parser functions
from parser import is_digital_pdf, extract_text_from_digital_pdf, pdf_to_base64_images

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API with the key from the environment variable
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Initialize the Gemini model as specified
model = genai.GenerativeModel("gemini-2.5-flash")

def extract_transactions_from_digital(text):
    """
    Sends the extracted text from a digital PDF to Gemini to extract bank transactions.
    We instruct the model to return ONLY a JSON array with specific keys.
    """
    prompt = f"""
    Please extract all bank transactions from the following text.
    Return ONLY a valid JSON array — no extra text, no markdown, no backticks.
    Each transaction object in the array must have these exact keys: 
    date, description, debit, credit, balance.
    If debit or credit is empty for a transaction, use null.
    
    Text:
    {text}
    """

    try:
        # Send the prompt to the Gemini model
        response = model.generate_content(prompt)
        
        # Clean the response text by removing potential markdown backticks
        raw_output = response.text.strip()
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:]
        if raw_output.startswith("```"):
            raw_output = raw_output[3:]
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3]
            
        raw_output = raw_output.strip()
        
        # Parse the cleaned text as JSON
        transactions = json.loads(raw_output)
        return transactions
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from Gemini response: {e}")
        print(f"Raw response was: {response.text}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during digital text extraction: {e}")
        return []


def extract_transactions_from_images(base64_images):
    """
    Sends base64 encoded images of a scanned PDF to Gemini Vision to extract bank transactions.
    We instruct the model to return ONLY a JSON array with specific keys.
    """
    prompt = """
    Please look at these bank statement images and extract all bank transactions.
    Return ONLY a valid JSON array — no extra text, no markdown, no backticks.
    Each item in the array must be an object with the following exact keys:
    date, description, debit, credit, balance.
    If debit or credit is empty for a transaction, use null.
    """
    
    try:
        # Build the message content as a list
        contents = []
        
        # First add each image as an inline_data part
        for img_base64 in base64_images:
            # The genai SDK supports dict representations of Blobs
            # We provide the mime_type and the base64 data
            image_part = {
                "mime_type": "image/jpeg",
                "data": img_base64
            }
            contents.append(image_part)
            
        # Add the text prompt at the end
        contents.append(prompt)
        
        # Send the list of contents to Gemini
        response = model.generate_content(contents)
        
        # Clean the response text by removing potential markdown backticks
        raw_output = response.text.strip()
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:]
        if raw_output.startswith("```"):
            raw_output = raw_output[3:]
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3]
            
        raw_output = raw_output.strip()
        
        # Parse the cleaned text as JSON
        transactions = json.loads(raw_output)
        return transactions
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from Gemini response: {e}")
        print(f"Raw response was: {response.text}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during image extraction: {e}")
        return []


def extract_transactions(file_path):
    """
    Main function that orchestrates the flow. It uses the parser to check if the PDF
    is digital or scanned, and routes it to the appropriate Gemini extraction function.
    """
    try:
        # Use our own parser to check the PDF type
        is_digital = is_digital_pdf(file_path)
        
        if is_digital:
            print(f"File '{os.path.basename(file_path)}' is a digital PDF. Extracting raw text...")
            # Extract raw text
            text = extract_text_from_digital_pdf(file_path)
            
            print("Sending raw text to Gemini for transaction extraction...")
            # Extract transactions from text
            transactions = extract_transactions_from_digital(text)
        else:
            print(f"File '{os.path.basename(file_path)}' is a scanned PDF. Converting pages to images...")
            # Get high-res base64 images
            base64_images = pdf_to_base64_images(file_path)
            
            print("Sending statement images to Gemini for transaction extraction...")
            # Extract transactions from vision
            transactions = extract_transactions_from_images(base64_images)
            
        return transactions
        
    except Exception as e:
        print(f"An error occurred in the main extract_transactions flow: {e}")
        return []
