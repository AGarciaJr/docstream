import sqlite3
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def setup_legacy_database():
    """Creates a mock Microsoft Access database using the updated 6-column schema."""
    db_name = 'legacy_parts.db'
    
    # Remove existing DB to prevent column mismatch errors
    if os.path.exists(db_name):
        os.remove(db_name)
        print("Cleaned up old legacy_parts.db")

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Updated table structure to match processor.py requirements
    cursor.execute('''CREATE TABLE IF NOT EXISTS parts 
                     (part_num TEXT, cert_id TEXT, status TEXT, 
                      source_file TEXT, jira_id TEXT, timestamp TEXT)''')
    
    # Pre-populate with legacy data
    # Jira ID and Timestamp start as empty/None for legacy records
    mock_data = [
        ("BAYLOR-2026-XP1", "CERT-999-ABC", "COMPLIANT", "legacy_record_01", None, None),
        ("MARATHON-NORCO-77", "CERT-444-XYZ", "COMPLIANT", "legacy_record_02", None, None),
        ("BU-BEARS-V8", "CERT-111-GRN", "NON-COMPLIANT", "legacy_record_03", None, None)
    ]
    
    cursor.executemany("INSERT INTO parts VALUES (?, ?, ?, ?, ?, ?)", mock_data)
    conn.commit()
    print("Legacy Database initialized with 6-column schema.")
    
    # Fetch records to generate the PDFs
    cursor.execute("SELECT part_num, cert_id FROM parts")
    records = cursor.fetchall()
    conn.close()
    return records

def create_pdf_cert(part_no, cert_id, filename):
    """Generates a PDF based on database records for the AI to process."""
    os.makedirs("scanner_inbox", exist_ok=True)
    filepath = f"scanner_inbox/{filename}.pdf"
    c = canvas.Canvas(filepath, pagesize=letter)
    
    # Document Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "MANUFACTURING QUALITY ASSURANCE")
    c.line(100, 745, 500, 745)
    
    # Dynamic Data
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, f"PART NUMBER: {part_no}")
    c.drawString(100, 680, f"CERTIFICATION ID: {cert_id}")
    c.drawString(100, 660, "INSPECTOR: BAYLOR-QA-TEAM")
    
    # Measurement Table for Quality Group demo
    c.drawString(100, 600, "Measurement Data:")
    c.rect(95, 540, 400, 50)
    c.drawString(105, 570, "Tolerance: +/- 0.05")
    c.drawString(105, 550, "Status: COMPLIANT")
    
    c.showPage()
    c.save()
    print(f"Generated PDF for scanning: {filepath}")

if __name__ == "__main__":
    records = setup_legacy_database()
    for i, (p_no, c_id) in enumerate(records):
        create_pdf_cert(p_no, c_id, f"part_scan_{i+1}")