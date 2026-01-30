# -*- coding: utf-8 -*-
import pdfplumber
import fitz  # PyMuPDF
import os
import re
from pathlib import Path

# Set paths - using absolute path
base_dir = Path(r'D:\VSCode\A_AI_Project\Anthropics_skills_git\gemdale-sh-cc-skills-main\Test_result')
pdf_path = base_dir / '【投资分析报告-路演网页多模态】松江区泗泾04-08号地块.pdf'
output_dir = base_dir / 'extracted_content'
images_dir = output_dir / 'images'
images_dir.mkdir(parents=True, exist_ok=True)

print(f"Processing PDF: {pdf_path}")
print(f"Output directory: {output_dir}")

# Extract text with pdfplumber
print("\n=== Extracting text content ===")
full_text = []

with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        print(f"Processing page {i+1}/{len(pdf.pages)}...")
        text = page.extract_text()
        if text:
            full_text.append(f"## Page {i+1}\n\n{text}\n")

# Save full markdown
full_md_path = output_dir / 'full.md'
with open(full_md_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(full_text))

print(f"\nSaved full.md to: {full_md_path}")

# Extract images with PyMuPDF
print("\n=== Extracting images ===")
pdf_document = fitz.open(pdf_path)
image_count = 0

for page_num in range(len(pdf_document)):
    page = pdf_document[page_num]
    image_list = page.get_images()

    for img_index, img in enumerate(image_list):
        xref = img[0]
        base_image = pdf_document.extract_image(xref)

        if base_image:
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = images_dir / f"page{page_num+1}_img{img_index+1}.{image_ext}"

            with open(image_filename, "wb") as img_file:
                img_file.write(image_bytes)

            image_count += 1
            print(f"Saved: {image_filename}")

pdf_document.close()
print(f"\nTotal images extracted: {image_count}")
print(f"Images saved to: {images_dir}")
print("\nDone!")
