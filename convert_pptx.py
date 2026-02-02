import os
import sys
import win32com.client

def pptx_to_pdf(pptx_path, pdf_path=None):
    """Convert PowerPoint to PDF using COM automation"""
    powerpoint = win32com.client.Dispatch("PowerPoint.Application")

    # Don't set Visible property to avoid the error
    # powerpoint.Visible = False  # Skip this

    if pdf_path is None:
        pdf_path = os.path.splitext(pptx_path)[0] + '.pdf'

    try:
        # Get absolute paths
        pptx_abs = os.path.abspath(pptx_path)
        pdf_abs = os.path.abspath(pdf_path)

        # Open and save
        deck = powerpoint.Presentations.Open(pptx_abs)
        deck.SaveAs(pdf_abs, 32)  # 32 = ppSaveAsPDF
        deck.Close()

        return pdf_abs
    finally:
        powerpoint.Quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_pptx.py <pptx_file> [pdf_file]")
        sys.exit(1)

    pptx_file = sys.argv[1]
    pdf_file = sys.argv[2] if len(sys.argv) > 2 else None

    result = pptx_to_pdf(pptx_file, pdf_file)
    print(f"Converted to: {result}")
