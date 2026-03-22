import gspread
from google.oauth2.credentials import Credentials

# Paste your copied ID here
SPREADSHEET_ID = '1fNOrk4kBvVjd11pu8eJJnihQLydiIuaW-hjkpGoAK6E'

def update_ledger(structured_data):
    """
    Connects to Google Sheets, calculates the new running balance, 
    and appends the new row.
    """
    print("📊 Connecting to Google Sheets...")
    
    # We authorize gspread using the token.json we already generated
    creds = Credentials.from_authorized_user_file('token.json')
    client = gspread.authorize(creds)
    
    # Open the first tab of the spreadsheet
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    
    # --- The Math Logic ---
    all_records = sheet.get_all_values()
    
    # Get the last running balance (defaults to 0.0 if the sheet only has headers)
    if len(all_records) > 1:
        try:
            # Assuming Balance is the 6th column (index 5)
            previous_balance = float(all_records[-1][5]) 
        except ValueError:
            previous_balance = 0.0
    else:
        previous_balance = 0.0
        
    amount = structured_data.amount
    
    # Route the money and calculate the new balance based on the LLM's classification
    if structured_data.transaction_category == "DEBIT":
        debit_val = amount
        credit_val = 0.0
        new_balance = previous_balance - amount
    else:
        debit_val = 0.0
        credit_val = amount
        new_balance = previous_balance + amount
        
    # Construct the row
    new_row = [
        structured_data.date, 
        structured_data.entity_name, 
        structured_data.description, 
        debit_val, 
        credit_val, 
        new_balance
    ]
    
    # Send to Google Sheets
    sheet.append_row(new_row)
    print(f"✅ Appended row: {structured_data.entity_name} | Balance updated to: {new_balance}")
    
    return True

# --- Quick Test Block ---
if __name__ == '__main__':
    from llm_processor import LedgerData
    
    print("Starting Sheets Ledger Test...")
    
    # We create a dummy object using your Pydantic schema to test the math
    dummy_data = LedgerData(
        date="2026-03-21",
        entity_name="Test Vendor Inc.",
        amount=250.00,
        transaction_category="CREDIT",
        description="Software License"
    )
    
    update_ledger(dummy_data)