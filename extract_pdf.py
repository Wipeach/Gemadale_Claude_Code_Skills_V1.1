import fitz  # PyMuPDF
import json
import os
from pathlib import Path

def extract_pdf_content(pdf_path, output_dir):
    """Extract text and images from PDF using PyMuPDF"""
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Open PDF
    doc = fitz.open(str(pdf_path))

    result = {
        "file_name": pdf_path.stem,
        "total_pages": len(doc),
        "pages": []
    }

    # Markdown content
    markdown_content = f"# {pdf_path.stem}\n\n"

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Extract text
        text = page.get_text()

        page_data = {
            "page_number": page_num + 1,
            "text": text
        }

        result["pages"].append(page_data)

        # Add to markdown
        markdown_content += f"## Page {page_num + 1}\n\n{text}\n\n---\n\n"

    # Save as JSON
    json_file = output_dir / f"{pdf_path.stem}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Save as Markdown
    md_file = output_dir / f"{pdf_path.stem}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    doc.close()

    print(f"Extracted {len(result['pages'])} pages")
    print(f"JSON saved to: {json_file}")
    print(f"Markdown saved to: {md_file}")

    return result

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python extract_pdf.py <pdf_file> [output_dir]")
        sys.exit(1)

    pdf_file = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "Test_result"

    extract_pdf_content(pdf_file, out_dir)
