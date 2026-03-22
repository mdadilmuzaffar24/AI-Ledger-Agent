import time
from auth import authenticate_google_apis
from gmail_ingestion import get_unread_invoice_pdfs, mark_as_read
from pdf_extractor import extract_text_from_pdf_bytes
from llm_processor import analyze_invoice_text
from sheets_ledger import update_ledger

def run_agent():
    print("🚀 Starting AI Ledger Agent...")
    gmail_svc, sheets_svc = authenticate_google_apis()
    pdfs = get_unread_invoice_pdfs(gmail_svc)
    
    if not pdfs:
        print("🛑 Agent finished: No new invoices to process.")
        return

    print(f"📦 Found {len(pdfs)} new email(s) with PDFs to process.\n")
    
    for pdf in pdfs:
        msg_id = pdf['msg_id']
        filename = pdf['filename']
        print(f"--- Processing File: {filename} ---")
        
        # Now returns a list of pages
        pages_text = extract_text_from_pdf_bytes(pdf['data'])
        
        if not pages_text:
            print(f"⚠️ Skipping {filename}: Could not extract any text.")
            continue
            
        all_pages_successful = True
        
        # Loop through each page in the Flipkart PDF as its own invoice
        for i, page_text in enumerate(pages_text):
            print(f"  📄 Analyzing Page {i+1} of {len(pages_text)}...")
            
            try:
                structured_data = analyze_invoice_text(page_text)
                success = update_ledger(structured_data)
                
                if not success:
                    all_pages_successful = False
                    
            except Exception as e:
                print(f"  ❌ Error processing Page {i+1}: {e}")
                all_pages_successful = False
                
            # Tiny delay to prevent hitting Groq's rate limits
            time.sleep(1)

        # Only mark the email as read if ALL pages inside the PDF succeeded
        if all_pages_successful:
            mark_as_read(gmail_svc, msg_id)
            print(f"🎉 Successfully processed ALL pages in {filename}!\n")
        else:
            print(f"⚠️ {filename} finished with some errors. Left unread in inbox.\n")

    print("🏁 All pending invoices processed.")

if __name__ == '__main__':
    run_agent()