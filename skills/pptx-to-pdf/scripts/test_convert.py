#!/usr/bin/env python3
"""
PPTX to PDF Converter - Windows COM Version

Uses Microsoft PowerPoint via COM automation for high-fidelity conversion.
This is the most reliable method on Windows systems with PowerPoint installed.
"""

import os
import sys
from pathlib import Path


def pptx_to_pdf_com(pptx_path: str, pdf_path: str = None) -> str:
    """
    Convert PPT/PPTX to PDF using PowerPoint COM automation.

    Supports both .ppt (legacy) and .pptx (modern) formats.

    Args:
        pptx_path: Path to input PowerPoint file (.ppt or .pptx)
        pdf_path: Path to output PDF file (optional, defaults to same name/location)

    Returns:
        Path to generated PDF file

    Raises:
        FileNotFoundError: If input file doesn't exist
        RuntimeError: If conversion fails
    """
    import win32com.client

    pptx_file = Path(pptx_path)

    if not pptx_file.exists():
        raise FileNotFoundError(f"Input file not found: {pptx_path}")

    # Determine output path
    if pdf_path is None:
        pdf_file = pptx_file.with_suffix(".pdf")
    else:
        pdf_file = Path(pdf_path)

    # Convert to absolute paths for COM
    pptx_absolute = str(pptx_file.absolute())
    pdf_absolute = str(pdf_file.absolute())

    print(f"Converting: {pptx_file.name}")
    print(f"Output: {pdf_file.name}")

    try:
        # Start PowerPoint
        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        powerpoint.Visible = False
        powerpoint.DisplayAlerts = 0

        try:
            # Open presentation
            # 1 = ReadOnly, Untitled = False, WithWindow = False
            deck = powerpoint.Presentations.Open(
                pptx_absolute,
                ReadOnly=1,
                Untitled=0,
                WithWindow=0
            )

            try:
                # Save as PDF
                # 32 = ppSaveAsPDF
                deck.SaveAs(pdf_absolute, 32)
                print("Conversion successful!")
                return str(pdf_file)

            finally:
                deck.Close()
        finally:
            powerpoint.Quit()

    except Exception as e:
        raise RuntimeError(f"Conversion failed: {e}")


def main():
    """Command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert PowerPoint to PDF using COM automation"
    )
    parser.add_argument("input", help="Input PPTX file")
    parser.add_argument("-o", "--output", help="Output PDF file")
    args = parser.parse_args()

    try:
        pdf_path = pptx_to_pdf_com(args.input, args.output)
        print(f"Created: {pdf_path}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
