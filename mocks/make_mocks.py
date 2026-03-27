import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

MOCK_PARTS = [
    ("MARATHON-NORCO-77",  "CERT-444-XYZ", "COMPLIANT"),
    ("MARATHON-NORCO-88",  "CERT-445-XYZ", "COMPLIANT"),
    ("MARATHON-NORCO-99",  "CERT-446-XYZ", "NON-COMPLIANT"),
    ("BAYLOR-2026-XP1",    "CERT-999-ABC", "COMPLIANT"),
    ("BAYLOR-2026-XP2",    "CERT-998-ABC", "COMPLIANT"),
    ("BAYLOR-2026-XP3",    "CERT-997-ABC", "NON-COMPLIANT"),
    ("BU-BEARS-V8",        "CERT-111-GRN", "NON-COMPLIANT"),
    ("BU-BEARS-V9",        "CERT-112-GRN", "COMPLIANT"),
    ("APEX-FRAME-4100",    "CERT-200-APX", "COMPLIANT"),
    ("APEX-FRAME-4200",    "CERT-201-APX", "COMPLIANT"),
    ("RIDGELINE-X1",       "CERT-300-RDG", "NON-COMPLIANT"),
    ("RIDGELINE-X2",       "CERT-301-RDG", "COMPLIANT"),
]

def create_pdf_cert(part_no, cert_id, status, filename):
    """Generates a realistic mock quality cert PDF for OCR scanning."""
    inbox_dir = os.path.join(os.path.dirname(__file__), '..', 'scanner_inbox')
    os.makedirs(inbox_dir, exist_ok=True)
    filepath = os.path.join(inbox_dir, f"{filename}.pdf")

    c = canvas.Canvas(filepath, pagesize=letter)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "MANUFACTURING QUALITY ASSURANCE")
    c.line(100, 745, 500, 745)

    c.setFont("Helvetica", 12)
    c.drawString(100, 700, f"PART NUMBER: {part_no}")
    c.drawString(100, 680, f"CERTIFICATION ID: {cert_id}")
    c.drawString(100, 660, "INSPECTOR: BAYLOR-QA-TEAM")

    c.drawString(100, 620, "Measurement Data:")
    c.rect(95, 555, 400, 58)
    c.drawString(105, 595, "Tolerance: +/- 0.05")
    c.drawString(105, 575, "Actual Deviation: 0.02")
    c.drawString(105, 558, f"Status: {status}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 520, f"Final Determination: {status}")

    c.showPage()
    c.save()

def generate_mock_inbox():
    """Fills scanner_inbox with a full batch of mock cert PDFs."""
    for i, (part_no, cert_id, status) in enumerate(MOCK_PARTS):
        create_pdf_cert(part_no, cert_id, status, f"part_scan_{i+1}")

if __name__ == "__main__":
    generate_mock_inbox()
    print(f"Generated {len(MOCK_PARTS)} mock PDFs into scanner_inbox/")
