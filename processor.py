import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os
import sqlite3
import re
import shutil
import pandas as pd
import datetime

def get_all_records():
    """Fetches all records for the Migration Auditor tab."""
    conn = sqlite3.connect('legacy_parts.db')
    df = pd.read_sql_query("SELECT * FROM parts", conn)
    conn.close()
    return df

def push_to_jira(part_data):
    """Simulates a Jira API call for the Atlassian migration."""
    mock_id = f"OPS-{hash(part_data['part_no'] + part_data['cert_id']) % 10000}"
    return mock_id

def update_local_db(part_data):
    """Updates legacy DB with Jira keys and timestamps."""
    conn = sqlite3.connect('legacy_parts.db')
    cursor = conn.cursor()
    # Ensure 6 columns exist: part_num, cert_id, status, source_file, jira_id, timestamp
    cursor.execute('''CREATE TABLE IF NOT EXISTS parts 
                     (part_num TEXT, cert_id TEXT, status TEXT, source_file TEXT, jira_id TEXT, timestamp TEXT)''')
    
    jira_id = push_to_jira(part_data)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("INSERT INTO parts VALUES (?, ?, ?, ?, ?, ?)", 
                  (part_data['part_no'], part_data['cert_id'], part_data['status'], part_data['file_name'], jira_id, timestamp))
    conn.commit()
    conn.close()
    return jira_id

def finalize_and_route(item_data):
    """Automates filing into specific part-number directories."""
    target_dir = os.path.join("processed_certs", item_data['part_no'])
    os.makedirs(target_dir, exist_ok=True)
    
    source_path = os.path.join("scanner_inbox", item_data['file_name'])
    target_path = os.path.join(target_dir, f"{item_data['cert_id']}.pdf")
    
    if os.path.exists(source_path):
        shutil.move(source_path, target_path)
        return target_path
    return None

def extract_data_from_scan(file_path):
    """Performs private, local OCR extraction."""
    pages = convert_from_path(file_path, 300)
    image = pages[0]
    raw_text = pytesseract.image_to_string(image)
    
    p_match = re.search(r"PART NUMBER:?\s*(.*)", raw_text, re.IGNORECASE)
    c_match = re.search(r"CERTIFICATION ID:?\s*(.*)", raw_text, re.IGNORECASE)
    
    return {
        "part_no": p_match.group(1).split('\n')[0].strip() if p_match else "NOT FOUND",
        "cert_id": c_match.group(1).split('\n')[0].strip() if c_match else "NOT FOUND",
        "status": "COMPLIANT" if "COMPLIANT" in raw_text.upper() else "NON-COMPLIANT",
        "file_name": os.path.basename(file_path),
        "raw_text": raw_text
    }

def process_batch(directory_path):
    results = []
    if os.path.exists(directory_path):
        for f in os.listdir(directory_path):
            if f.endswith(('.pdf', '.png', '.jpg')):
                results.append(extract_data_from_scan(os.path.join(directory_path, f)))
    return results