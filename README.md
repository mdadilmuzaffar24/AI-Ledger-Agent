# 🤖 AI Automated Ledger Agent

An intelligent, serverless Python automation pipeline that monitors a Gmail inbox for PDF invoices, extracts unstructured text in-memory, and uses a Large Language Model (Llama 3.1) to structure the data and autonomously update a Google Sheets general ledger.

## 🌟 Architecture Overview

1. **Ingestion (Gmail API):** Authenticates securely via OAuth 2.0 and queries the inbox for unread emails containing attachments.
2. **In-Memory Processing (`pdfplumber`):** Downloads PDF byte streams and extracts raw text directly in RAM, avoiding local storage clutter.
3. **Intelligent Structuring (Groq + Llama 3.1):** Passes unstructured text to Llama 3.1. Uses the `instructor` library and Pydantic schemas to strictly enforce valid JSON outputs for entity extraction and transaction classification (Debit vs. Credit).
4. **Ledger Synchronization (Google Sheets API):** Calculates running balances based on AI classifications and pushes the formatted row to a live Google Sheet, finally marking the origin email as 'Read'.

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **AI/LLM:** Llama 3.1 (via Groq API for ultra-fast inference)
* **Structuring:** Pydantic, Instructor
* **Cloud APIs:** Google Workspace (Gmail API, Google Sheets API)
* **Data Handling:** `pdfplumber`, `gspread`

## 🚀 Future Roadmap
* Implement a front-end UI for manual invoice uploads and live ledger viewing.
* Add Multimodal/OCR fallback for scanned, non-text PDFs.