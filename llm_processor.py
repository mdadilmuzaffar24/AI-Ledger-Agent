import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import instructor
from groq import Groq

# Load the environment variables from the .env file
load_dotenv()

# Initialize the Groq client and patch it with instructor to force JSON output
client = instructor.from_groq(Groq(api_key=os.environ.get("GROQ_API_KEY")))

class LedgerData(BaseModel):
    date: str = Field(description="The date of the invoice (e.g., YYYY-MM-DD)")
    entity_name: str = Field(description="The name of the vendor, client, or company")
    amount: float = Field(description="The final total amount as a float (e.g., 150.50). Do not include currency symbols.")
    transaction_category: str = Field(description="Strictly classify as 'CREDIT' if the invoice is a bill to be paid by us (Money Out). Classify as 'DEBIT' if it is an invoice we sent to a client for payment (Money In).")
    description: str = Field(description="A brief 3-5 word description of the items or services")

def analyze_invoice_text(invoice_text: str) -> LedgerData:
    """
    Sends the raw extracted PDF text to Llama 3.1 via Groq.
    Forces the LLM to return a structured Python object matching LedgerData.
    """
    print("🧠 Sending unstructured text to Llama 3.1...")
    
    # We are using Llama 3.1 8B for lightning-fast structured output
    extracted_data = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        response_model=LedgerData,
        messages=[
            {
                "role": "system", 
                "content": "You are an expert financial data extraction AI. Extract the requested fields from the invoice text. You MUST return strictly valid JSON. Never use single quotes for strings, only use double quotes."
            },
            {
                "role": "user", 
                "content": f"Here is the raw text from the PDF:\n\n{invoice_text}"
            }
        ]
    )
    
    return extracted_data

# --- Quick Test Block ---
if __name__ == '__main__':
    from auth import authenticate_google_apis
    from gmail_ingestion import get_unread_invoice_pdfs
    from pdf_extractor import extract_text_from_pdf_bytes
    
    print("Starting AI Extraction Test...")
    gmail_svc, _ = authenticate_google_apis()
    pdfs = get_unread_invoice_pdfs(gmail_svc)
    
    if pdfs:
        print(f"Extracting text from: {pdfs[0]['filename']}")
        text = extract_text_from_pdf_bytes(pdfs[0]['data'])
        
        if text:
            # Pass the text to Llama 3.1
            structured_data = analyze_invoice_text(text)
            
            print("\n✅ --- LLM STRUCTURED OUTPUT ---")
            print(f"Date:       {structured_data.date}")
            print(f"Entity:     {structured_data.entity_name}")
            print(f"Amount:     ${structured_data.amount}")
            print(f"Category:   {structured_data.transaction_category}")
            print(f"Desc:       {structured_data.description}")
            print("---------------------------------")