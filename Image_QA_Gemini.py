import streamlit as st
from dotenv import load_dotenv
import os
from PIL import Image
import google.generativeai as genai
import pdfplumber  # For extracting text from PDF
import json
import re

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define user question for the invoice extraction
user_question = """
Extract invoice information like invoice_no, invoice_date, grand_total, and barcode_no (a 13-digit number from the top left corner) out of this PDF file. 
Return the results in the following JSON format:

{
  "fields": [
    {
      "field": "Invoice No.",
      "value": "23",
      "bounding_box": [230, 667, 245, 678],
      "page": 0
    },
    {
      "field": "invoice_date",
      "value": "30-09-2024",
      "bounding_box": [120, 112, 138, 219],
      "page": 1
    }
  ],
  "accuracy": 0.99,
  "total_fields": 14,
  "fields_extracted": 13
}
"""

# Helper function to extract information from a PDF
def extract_invoice_info(pdf_file):
    extracted_data = {
        "fields": [],
        "total_fields": 4,  # Update as needed if you expect more fields
        "fields_extracted": 0,
        "accuracy": 0.0
    }

    try:
        # Use pdfplumber to read the PDF
        with pdfplumber.open(pdf_file) as pdf:
            for page_number, page in enumerate(pdf.pages):
                text = page.extract_text()
                
                # Example: Extract invoice number
                invoice_no = re.search(r"Invoice No\.\s*(\d+)", text)
                if invoice_no:
                    extracted_data["fields"].append({
                        "field": "Invoice No.",
                        "value": invoice_no.group(1),
                        "bounding_box": [],  # Use OCR for this if needed
                        "page": page_number
                    })
                    extracted_data["fields_extracted"] += 1

                # Example: Extract invoice date
                invoice_date = re.search(r"Date\s*[:\s]*([\d-]+)", text)
                if invoice_date:
                    extracted_data["fields"].append({
                        "field": "invoice_date",
                        "value": invoice_date.group(1),
                        "bounding_box": [],  # Use OCR for this if needed
                        "page": page_number
                    })
                    extracted_data["fields_extracted"] += 1

                # Example: Extract grand total
                grand_total = re.search(r"Grand Total\s*[:\s]*([\d.,]+)", text)
                if grand_total:
                    extracted_data["fields"].append({
                        "field": "grand_total",
                        "value": grand_total.group(1),
                        "bounding_box": [],  # Use OCR for this if needed
                        "page": page_number
                    })
                    extracted_data["fields_extracted"] += 1

                # Example: Extract barcode number (13-digit)
                barcode_no = re.search(r"\b\d{13}\b", text)
                if barcode_no:
                    extracted_data["fields"].append({
                        "field": "barcode_no",
                        "value": barcode_no.group(0),
                        "bounding_box": [],  # Use OCR for this if needed
                        "page": page_number
                    })
                    extracted_data["fields_extracted"] += 1

        # Calculate accuracy as a simple ratio (if applicable)
        extracted_data["accuracy"] = extracted_data["fields_extracted"] / extracted_data["total_fields"]

    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")

    return extracted_data

# Main app function
def show():    
    st.header("Image & PDF QA")

    # Text input
    user_input = st.text_input("Input Prompt: ", key="input")
    
    # File uploader for image or PDF
    file = st.file_uploader("Choose an image or PDF...", type=["jpg", "jpeg", "png", "pdf"])
    image = None
    pdf_data = None

    if file is not None:
        if file.type == "application/pdf":
            pdf_data = file
            st.write("PDF Uploaded!")
        else:
            image = Image.open(file)
            st.image(image, caption="Uploaded Image", use_column_width=True)

    # Submit button
    submit = st.button("Submit")

    if submit:
        if pdf_data:
            # Extract information from PDF
            extracted_info = extract_invoice_info(pdf_data)
            st.subheader("Extracted Invoice Information")
            st.json(extracted_info)
        elif user_input and image:
            # If using the generative model with image and text input
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content([user_input, image])
            st.subheader("The Response is")
            st.write(response.text)
        elif image:
            # If only image is provided
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(image)
            st.subheader("The Response is")
            st.write(response.text)
        else:
            st.warning("Please provide either a PDF file, input prompt, or an image.")
