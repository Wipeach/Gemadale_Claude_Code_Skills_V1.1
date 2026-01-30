import win32com.client
import os
import sys

def pptx_to_pdf(pptx_path, pdf_path=None):
    """Convert PPTX to PDF using PowerPoint COM"""
    if pdf_path is None:
        pdf_path = os.path.splitext(pptx_path)[0] + '.pdf'

    pptx_path = os.path.abspath(pptx_path)
    pdf_path = os.path.abspath(pdf_path)

    print(f"Converting:")
    print(f"  From: {pptx_path}")
    print(f"  To: {pdf_path}")

    try:
        powerpoint = win32com.client.Dispatch("PowerPoint.Application")

        deck = powerpoint.Presentations.Open(pptx_path)
        deck.SaveAs(pdf_path, 32)  # 32 = ppSaveAsPDF
        deck.Close()

        powerpoint.Quit()

        print(f"\nSuccess! PDF created at:")
        print(f"  {pdf_path}")
        return True

    except Exception as e:
        print(f"\nError: {e}")
        return False

if __name__ == "__main__":
    pptx_file = r"Test_result\【投资分析报告-路演网页多模态】松江区泗泾04-08号地块.pptx"
    pptx_to_pdf(pptx_file)
