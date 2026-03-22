# 🤖 AI Automated Ledger Agent

An end-to-end, serverless Python data pipeline that autonomously monitors an inbox, extracts unstructured data from complex multi-page PDF invoices, and uses **Llama 3.1** to strictly structure the data before syncing it to a live Google Sheets general ledger.

## 🌟 Live Demo & Dashboard
* **https://ai-ledger-agent.streamlit.app/**
* **[View the Deployed Streamlit UI Here](#)**

## 🏗️ System Architecture

1. **Cloud Ingestion (Gmail API):** Authenticates securely via OAuth 2.0. Queries the inbox for unread emails with attachments, acting as an immutable ingestion queue.
2. **In-Memory Extraction (`pdfplumber`):** Streams raw PDF bytes directly into RAM without saving to local disk. Splices multi-page consolidated invoices (e.g., e-commerce receipts with separate shipping/fee pages) into distinct chronological documents.
3. **Intelligent Structuring (Llama 3.1 + Groq):** * Utilizes Llama 3.1 8B via Groq for ultra-low latency inference.
   * Leverages the `instructor` library and `Pydantic` schemas to strictly enforce valid JSON outputs, ensuring mathematical safety (e.g., preventing LLMs from returning string equations like `"300+50"` instead of floats).
4. **Database Synchronization (Google Sheets API):** Calculates running balances in Python and pushes the structured row to the ledger. Finally, marks the origin email as 'Read' to close the loop.

## 🛠️ Tech Stack
* **Language:** Python 3.11+
* **AI/LLM:** Llama 3.1 8B (via Groq)
* **Structuring:** Pydantic, Instructor
* **Cloud APIs:** Google Workspace (Gmail API, Google Sheets API)
* **Frontend UI:** Streamlit, Pandas

## 💡 Overcoming Engineering Challenges
**The Consolidated Multi-Page PDF Problem:** Initial tests revealed that e-commerce vendors often bundle multiple distinct transactions (e.g., primary item, platform fees, shipping) into a single multi-page PDF. Passing the entire document to the LLM caused context confusion and missed line items. 
* **Solution:** Refactored the extraction module to yield a list of page-specific text buffers, iterating the LLM over each page individually. This ensured 100% extraction accuracy across complex, heavily formatted corporate invoices.
