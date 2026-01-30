---
name: pptx-to-pdf
description: "Convert PowerPoint presentations (.ppt and .pptx) to PDF format with high fidelity. Supports both legacy and modern formats, batch conversion, custom page settings, and preserves formatting, fonts, layouts, and embedded media."
license: Proprietary
---

# PowerPoint to PDF Conversion Guide

## Overview

This skill provides comprehensive tools and workflows for converting PowerPoint presentations to PDF format. Supports both legacy (.ppt) and modern (.pptx) formats. PDF conversion is essential for:
- Sharing presentations in a universal format
- Preserving slide design and formatting
- Creating print-ready documents
- Archiving presentations
- Ensuring consistent rendering across devices

## Quick Start

### Windows (Recommended - PowerPoint COM)
```python
# Using the provided script
python scripts/test_convert.py presentation.pptx

# With custom output name
python scripts/test_convert.py presentation.pptx -o output.pdf
```

### Cross-Platform (LibreOffice)
```bash
# Basic conversion using LibreOffice
soffice --headless --convert-to pdf presentation.pptx

# Specify output directory
soffice --headless --convert-to pdf --outdir output/ presentation.pptx
```

### Batch Conversion
```bash
# Convert all PPTX files in current directory
for file in *.pptx; do
    soffice --headless --convert-to pdf "$file"
done
```

## Methods

### Method 1: PowerPoint COM Automation (Windows - Recommended)

**Best option for Windows users with Microsoft PowerPoint installed.**
Provides highest fidelity conversion with perfect formatting preservation.

#### Requirements
- Microsoft PowerPoint installed (any version 2010+)
- Python with pywin32: `pip install pywin32`

#### Usage

**Single file conversion:**
```python
import win32com.client

def pptx_to_pdf(pptx_path, pdf_path=None):
    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    powerpoint.Visible = False

    if pdf_path is None:
        pdf_path = pptx_path.replace('.pptx', '.pdf')

    deck = powerpoint.Presentations.Open(pptx_path)
    deck.SaveAs(pdf_path, 32)  # 32 = ppSaveAsPDF
    deck.Close()
    powerpoint.Quit()

    return pdf_path

# Use it
pptx_to_pdf("presentation.pptx", "output.pdf")
```

**Using the provided script:**
```bash
python scripts/test_convert.py presentation.pptx
python scripts/test_convert.py presentation.pptx -o custom_name.pdf
```

### Method 2: LibreOffice (Cross-Platform)
**Windows:**
```bash
# Download and install from https://www.libreoffice.org/download/
# Or use chocolatey
choco install libreoffice
```

**Linux:**
```bash
sudo apt-get install libreoffice
```

**macOS:**
```bash
brew install --cask libreoffice
```

#### Basic Usage
```bash
soffice --headless --convert-to pdf input.pptx
```

#### Advanced Options
```bash
# Convert to specific PDF version (PDF/A-1b, PDF/A-2b, etc.)
soffice --headless --convert-to pdf:writer_pdf_Export \
    --outdir output/ \
    input.pptx

# Export with specific settings
soffice --headless --convert-to pdf \
    --infilter="Impress MS PowerPoint 2007 XML" \
    input.pptx
```

### Method 2: Python (python-pptx + reportlab)

For programmatic conversion with custom processing.

```python
from pptx import Presentation
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os

def pptx_to_pdf_basic(pptx_path, pdf_path):
    """Basic conversion - creates PDF with slide content as text"""
    prs = Presentation(pptx_path)

    # Create PDF
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch

    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    for slide_num, slide in enumerate(prs.slides):
        # Extract text from slide
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text = shape.text
                y_pos = height - (1 * inch) - (slide_num * 100)
                c.drawString(1 * inch, y_pos, text)

        c.showPage()

    c.save()
```

### Method 3: COM Automation (Windows Only)

Uses Microsoft PowerPoint via COM for highest fidelity on Windows.

```python
import win32com.client
import os

def pptx_to_pdf_com(pptx_path, pdf_path):
    """Convert using PowerPoint COM (Windows only)"""
    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    powerpoint.Visible = False

    try:
        deck = powerpoint.Presentations.Open(os.path.abspath(pptx_path))
        deck.SaveAs(os.path.abspath(pdf_path), 32)  # 32 = ppSaveAsPDF
        deck.Close()
    finally:
        powerpoint.Quit()
```

### Method 4: Cloud Conversion API

For cloud-based conversion without local dependencies.

```python
import requests

def convert_with_api(pptx_path, api_key):
    """Example using a cloud conversion service"""
    url = "https://api.conversion-service.com/convert"

    with open(pptx_path, 'rb') as f:
        files = {'file': f}
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.post(url, files=files, headers=headers)

    if response.status_code == 200:
        with open('output.pdf', 'wb') as f:
            f.write(response.content)
```

## Batch Processing Scripts

### Convert Multiple Files
```python
import os
import subprocess
from pathlib import Path

def batch_convert_pptx_to_pdf(input_dir, output_dir=None):
    """Convert all PPTX files in a directory"""
    input_path = Path(input_dir)
    output_path = Path(output_dir) if output_dir else input_path

    output_path.mkdir(parents=True, exist_ok=True)

    pptx_files = list(input_path.glob("*.pptx")) + list(input_path.glob("*.PPTX"))

    for pptx_file in pptx_files:
        pdf_file = output_path / f"{pptx_file.stem}.pdf"

        print(f"Converting {pptx_file.name}...")
        subprocess.run([
            "soffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(output_path),
            str(pptx_file)
        ])
        print(f"  -> {pdf_file.name}")

# Usage
batch_convert_pptx_to_pdf("presentations/", "output_pdfs/")
```

### Recursive Directory Conversion
```python
def convert_recursive(root_dir):
    """Convert PPTX files in all subdirectories"""
    for pptx_file in Path(root_dir).rglob("*.pptx"):
        # Preserve directory structure
        relative_path = pptx_file.relative_to(root_dir)
        output_file = Path(root_dir) / "pdfs" / relative_path.with_suffix(".pdf")

        output_file.parent.mkdir(parents=True, exist_ok=True)

        subprocess.run([
            "soffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(output_file.parent),
            str(pptx_file)
        ])
```

## Quality Settings

### High Quality (Print Ready)
```bash
soffice --headless --convert-to pdf \
    --infilter="Impress MS PowerPoint 2007 XML" \
    presentation.pptx
```

### Compressed (Web/Email)
```bash
# Requires post-processing with ghostscript
gs -sDEVICE=pdfwrite \
   -dCompatibilityLevel=1.4 \
   -dPDFSETTINGS=/ebook \
   -dNOPAUSE -dQUIET -dBATCH \
   -sOutputFile=compressed.pdf \
   presentation.pdf
```

### PDF/A Compliance (Archival)
```bash
soffice --headless --convert-to pdf:writer_pdf_Export \
    --outdir output/ \
    presentation.pptx
```

## Troubleshooting

### Fonts Not Rendering
```bash
# Install missing fonts on Linux
sudo apt-get install fonts-liberation

# On macOS, fonts are usually auto-included
# On Windows, ensure fonts are installed in C:\Windows\Fonts\
```

### Images Not Appearing
```bash
# Ensure media links are embedded, not external
# Convert with full path resolution
soffice --headless --convert-to pdf \
    /full/path/to/presentation.pptx
```

### Conversion Hangs
```bash
# Add timeout
timeout 300 soffice --headless --convert-to pdf presentation.pptx
```

### Layout Issues
- **Problem**: Text reflows incorrectly
- **Solution**: Use COM automation on Windows or ensure fonts are installed

- **Problem**: Slides are cut off
- **Solution**: Check page size settings in original PPTX

## Best Practices

1. **Test Conversion First**: Always convert a sample slide before batch processing
2. **Verify Output**: Check the PDF for formatting issues
3. **Use Absolute Paths**: Avoid path resolution issues
4. **Handle Errors**: Implement error handling in scripts
5. **Clean Up**: Remove temporary files after conversion

## Quick Reference

| Task | Command |
|------|---------|
| Single file | `soffice --headless --convert-to pdf file.pptx` |
| Batch convert | Loop with soffice command |
| Windows COM | Use python-win32com |
| High quality | Default LibreOffice output |
| Compressed | Post-process with Ghostscript |
| PDF/A | Use writer_pdf_Export filter |
