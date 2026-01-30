#!/usr/bin/env python3
"""
PPTX to PDF Converter

A utility script for converting PowerPoint presentations to PDF format.
Supports single file conversion, batch processing, and recursive directory conversion.

Requirements:
    - LibreOffice installed and available in PATH
    - Python 3.6+
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Optional


class PPTXConverter:
    """Converter class for PPTX to PDF conversion using LibreOffice."""

    def __init__(self, libreoffice_path: Optional[str] = None):
        """
        Initialize the converter.

        Args:
            libreoffice_path: Path to LibreOffice executable (optional)
        """
        self.libreoffice_cmd = self._find_libreoffice(libreoffice_path)

    def _find_libreoffice(self, custom_path: Optional[str] = None) -> str:
        """Find LibreOffice executable."""
        if custom_path and os.path.exists(custom_path):
            return custom_path

        # Common LibreOffice command names
        commands = ["soffice", "libreoffice", "loffice"]

        for cmd in commands:
            try:
                subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    check=True,
                    timeout=5
                )
                return cmd
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

        raise RuntimeError(
            "LibreOffice not found. Please install LibreOffice:\n"
            "  - Windows: Download from https://www.libreoffice.org/\n"
            "  - Linux: sudo apt-get install libreoffice\n"
            "  - macOS: brew install --cask libreoffice"
        )

    def convert_file(
        self,
        pptx_path: str,
        output_dir: Optional[str] = None,
        pdf_version: str = "pdf"
    ) -> str:
        """
        Convert a single PPTX file to PDF.

        Args:
            pptx_path: Path to input PPTX file
            output_dir: Output directory (default: same as input)
            pdf_version: PDF format version

        Returns:
            Path to generated PDF file
        """
        pptx = Path(pptx_path)

        if not pptx.exists():
            raise FileNotFoundError(f"Input file not found: {pptx_path}")

        if pptx.suffix.lower() not in [".pptx", ".pptm"]:
            raise ValueError(f"Not a PowerPoint file: {pptx_path}")

        # Determine output directory
        if output_dir:
            out_path = Path(output_dir)
            out_path.mkdir(parents=True, exist_ok=True)
        else:
            out_path = pptx.parent

        # Build command
        cmd = [
            self.libreoffice_cmd,
            "--headless",
            "--convert-to", pdf_version,
            "--outdir", str(out_path),
            str(pptx.absolute())
        ]

        # Run conversion
        print(f"Converting {pptx.name}...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            raise RuntimeError(f"Conversion failed: {result.stderr}")

        # Return PDF path
        pdf_path = out_path / f"{pptx.stem}.pdf"
        if pdf_path.exists():
            print(f"  -> {pdf_path}")
            return str(pdf_path)
        else:
            raise RuntimeError(f"PDF not created: {pdf_path}")

    def convert_batch(
        self,
        input_dir: str,
        output_dir: Optional[str] = None,
        pattern: str = "*.pptx"
    ) -> List[str]:
        """
        Convert all PPTX files in a directory.

        Args:
            input_dir: Input directory path
            output_dir: Output directory (default: same as input)
            pattern: File pattern to match

        Returns:
            List of generated PDF paths
        """
        input_path = Path(input_dir)
        if not input_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {input_dir}")

        output_path = Path(output_dir) if output_dir else input_path
        output_path.mkdir(parents=True, exist_ok=True)

        # Find all PPTX files
        pptx_files = (
            list(input_path.glob(pattern)) +
            list(input_path.glob(pattern.upper()))
        )
        pptx_files = list(set(pptx_files))  # Remove duplicates

        if not pptx_files:
            print(f"No PPTX files found in {input_dir}")
            return []

        # Convert each file
        pdf_files = []
        for pptx_file in pptx_files:
            try:
                pdf_path = self.convert_file(
                    str(pptx_file),
                    str(output_path)
                )
                pdf_files.append(pdf_path)
            except Exception as e:
                print(f"  ERROR: {e}")

        return pdf_files

    def convert_recursive(
        self,
        root_dir: str,
        output_base: str
    ) -> List[str]:
        """
        Convert PPTX files in all subdirectories, preserving structure.

        Args:
            root_dir: Root directory to search
            output_base: Base output directory

        Returns:
            List of generated PDF paths
        """
        root_path = Path(root_dir)
        output_path = Path(output_base)

        if not root_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {root_dir}")

        pdf_files = []

        for pptx_file in root_path.rglob("*.pptx"):
            # Preserve directory structure
            relative_path = pptx_file.relative_to(root_path)
            output_file = output_path / relative_path.with_suffix(".pdf")

            output_file.parent.mkdir(parents=True, exist_ok=True)

            try:
                pdf_path = self.convert_file(
                    str(pptx_file),
                    str(output_file.parent)
                )
                pdf_files.append(pdf_path)
            except Exception as e:
                print(f"  ERROR: {e}")

        return pdf_files


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Convert PowerPoint presentations to PDF"
    )

    parser.add_argument(
        "input",
        help="Input PPTX file or directory"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output directory (default: same as input)"
    )

    parser.add_argument(
        "-b", "--batch",
        action="store_true",
        help="Convert all PPTX files in input directory"
    )

    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Recursively convert all PPTX files"
    )

    parser.add_argument(
        "--libreoffice",
        help="Path to LibreOffice executable"
    )

    args = parser.parse_args()

    # Initialize converter
    converter = PPTXConverter(args.libreoffice)

    try:
        if args.recursive:
            pdf_files = converter.convert_recursive(
                args.input,
                args.output or "pdfs"
            )
        elif args.batch:
            pdf_files = converter.convert_batch(
                args.input,
                args.output
            )
        else:
            pdf_path = converter.convert_file(
                args.input,
                args.output
            )
            pdf_files = [pdf_path]

        print(f"\nConverted {len(pdf_files)} file(s)")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
