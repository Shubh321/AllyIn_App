import fitz  # from PyMuPDF
import email
from email import policy
import json
import os

# List to store parsed documents
parsed_docs = []

# --- PDF Parsing Function ---
def parse_pdf(file_path):
    with fitz.open(file_path) as doc:
        text = "".join(page.get_text() for page in doc)
    parsed_docs.append({
        "doc_id": os.path.basename(file_path),
        "source_type": "pdf",
        "title": os.path.basename(file_path),
        "body": text,
        "created_at": "2024-12-01"  # You can customize this
    })

# --- EML Email Parsing Function ---
def parse_eml(file_path):
    with open(file_path, 'rb') as f:
        msg = email.message_from_binary_file(f, policy=policy.default)
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body += part.get_content()
    else:
        body = msg.get_content()

    parsed_docs.append({
        "doc_id": os.path.basename(file_path),
        "source_type": "email",
        "title": msg.get('Subject', 'No Subject'),
        "body": body,
        "created_at": msg.get('Date', 'Unknown Date')
    })

# --- Example Usage ---
# Put test files in AllyIn/data/ before running this
parse_pdf('../data/sample.pdf')
parse_eml('../data/sample.eml')

# --- Save output to JSONL ---
output_path = 'parsed_docs.jsonl'
with open(output_path, 'w', encoding='utf-8') as f:
    for doc in parsed_docs:
        f.write(json.dumps(doc) + '\n')

print(f"✅ Parsed {len(parsed_docs)} documents. Output saved to {output_path}")
