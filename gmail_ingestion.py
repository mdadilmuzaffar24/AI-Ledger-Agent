import base64

def get_unread_invoice_pdfs(gmail_service):
    """Searches for unread emails with attachments and downloads the PDFs."""
    print("🔍 Searching for unread emails with attachments...")
    
    # Query: strictly unread emails that contain an attachment
    results = gmail_service.users().messages().list(userId='me', q="is:unread has:attachment").execute()
    messages = results.get('messages', [])
    
    if not messages:
        print("📭 No unread messages with attachments found.")
        return []

    pdf_data_list = []
    
    for message in messages:
        msg = gmail_service.users().messages().get(userId='me', id=message['id']).execute()
        
        # Navigate through the email payload to find the PDF parts
        parts = msg['payload'].get('parts', [])
        for part in parts:
            if part['mimeType'] == 'application/pdf':
                attachment_id = part['body'].get('attachmentId')
                
                if attachment_id:
                    # Fetch the actual file data
                    attachment = gmail_service.users().messages().attachments().get(
                        userId='me', messageId=message['id'], id=attachment_id
                    ).execute()
                    
                    # Google returns the file as a base64 string, so we decode it into raw bytes
                    file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                    filename = part.get('filename', 'unknown_invoice.pdf')
                    
                    pdf_data_list.append({
                        "msg_id": message['id'], 
                        "data": file_data,
                        "filename": filename
                    })
                    print(f"📥 Downloaded PDF: {filename}")
                    
    return pdf_data_list

def mark_as_read(gmail_service, msg_id):
    """Removes the UNREAD label from an email."""
    gmail_service.users().messages().modify(
        userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}
    ).execute()
    print(f"✅ Marked message {msg_id} as read.")

# --- Quick Test Block ---
if __name__ == '__main__':
    from auth import authenticate_google_apis
    print("Starting Gmail Ingestion Test...")
    gmail_svc, sheets_svc = authenticate_google_apis()
    
    pdfs = get_unread_invoice_pdfs(gmail_svc)
    print(f"Total PDFs temporarily stored in memory: {len(pdfs)}")