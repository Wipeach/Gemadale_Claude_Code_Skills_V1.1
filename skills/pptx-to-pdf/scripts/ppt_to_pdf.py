#!/usr/bin/env python3
"""
PowerPoint to PDF Converter - Windows COM Version

Supports both legacy .ppt and modern .pptx formats.
Uses Microsoft PowerPoint via COM automation for high-fidelity conversion.
"""

import os
import sys
from pathlib import Path
import argparse


class PowerPointConverter:
    """Converter class for PowerPoint to PDF conversion using COM automation."""

    SUPPORTED_FORMATS = ['.ppt', '.pptx', '.pptm', '.pps', '.ppsx']

    def __init__(self):
        """Initialize the converter by checking PowerPoint availability."""
        try:
            import win32com.client
            self.win32 = win32com.client
            # Test PowerPoint availability
            app = self.win32.Dispatch("PowerPoint.Application")
            app.Quit()
        except ImportError:
            raise RuntimeError(
                "pywin32 is required. Install with: pip install pywin32"
            )
        except Exception as e:
            raise RuntimeError(
                f"Microsoft PowerPoint not available: {e}\n"
                "Please ensure PowerPoint is installed."
            )

    def convert_file(
        self,
        ppt_path: str,
        pdf_path: str = None
    ) -> str:
        """
        Convert a PowerPoint file (.ppt or .pptx) to PDF.

        Args:
            ppt_path: Path to input PowerPoint file
            pdf_path: Path to output PDF file (optional)

        Returns:
            Path to generated PDF file

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If file format is not supported
            RuntimeError: If conversion fails
        """
        ppt_file = Path(ppt_path)

        if not ppt_file.exists():
            raise FileNotFoundError(f"Input file not found: {ppt_path}")

        if ppt_file.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {ppt_file.suffix}\n"
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        # Determine output path
        if pdf_path is None:
            pdf_file = ppt_file.with_suffix('.pdf')
        else:
            pdf_file = Path(pdf_path)

        # Convert to absolute paths for COM
        ppt_absolute = str(ppt_file.absolute())
        pdf_absolute = str(pdf_file.absolute())

        print(f"Converting: {ppt_file.name} ({ppt_file.suffix})")
        print(f"Output: {pdf_file.name}")

        try:
            # Start PowerPoint
            powerpoint = self.win32.Dispatch("PowerPoint.Application")
            # Note: Visible=False may not work in some PowerPoint versions/configurations
            # powerpoint.Visible = False
            powerpoint.DisplayAlerts = 0

            try:
                # Open presentation
                # ReadOnly=1, Untitled=0, WithWindow=0
                deck = powerpoint.Presentations.Open(
                    ppt_absolute,
                    ReadOnly=1,
                    Untitled=0,
                    WithWindow=0
                )

                try:
                    # Save as PDF
                    # 32 = ppSaveAsPDF
                    deck.SaveAs(pdf_absolute, 32)
                    print(f"[OK] Conversion successful!")
                    return str(pdf_file)

                finally:
                    deck.Close()
            finally:
                powerpoint.Quit()

        except Exception as e:
            raise RuntimeError(f"Conversion failed: {e}")

    def convert_batch(
        self,
        input_dir: str,
        output_dir: str = None,
        recursive: bool = False
    ) -> list:
        """
        Convert all PowerPoint files in a directory.

        Args:
            input_dir: Input directory path
            output_dir: Output directory (default: same as input)
            recursive: Process subdirectories recursively

        Returns:
            List of successfully converted PDF file paths
        """
        input_path = Path(input_dir)

        if not input_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {input_dir}")

        # Find all PowerPoint files
        if recursive:
            ppt_files = []
            for ext in self.SUPPORTED_FORMATS:
                ppt_files.extend(input_path.rglob(f"*{ext}"))
                ppt_files.extend(input_path.rglob(f"*{ext.upper()}"))
        else:
            ppt_files = []
            for ext in self.SUPPORTED_FORMATS:
                ppt_files.extend(input_path.glob(f"*{ext}"))
                ppt_files.extend(input_path.glob(f"*{ext.upper()}"))

        # Remove duplicates and sort
        ppt_files = sorted(set(ppt_files))

        if not ppt_files:
            print(f"No PowerPoint files found in {input_dir}")
            return []

        print(f"Found {len(ppt_files)} PowerPoint file(s)")

        # Set output directory
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = None

        # Convert each file
        pdf_files = []
        failed_files = []

        for i, ppt_file in enumerate(ppt_files, 1):
            print(f"\n[{i}/{len(ppt_files)}] ", end="")

            try:
                if output_path:
                    pdf_path = output_path / f"{ppt_file.stem}.pdf"
                else:
                    pdf_path = None

                pdf_file = self.convert_file(str(ppt_file), str(pdf_path) if pdf_path else None)
                pdf_files.append(pdf_file)

            except Exception as e:
                print(f"[X] Failed: {e}")
                failed_files.append((str(ppt_file), str(e)))

        # Summary
        print(f"\n{'='*60}")
        print(f"Conversion Summary:")
        print(f"  Successful: {len(pdf_files)}")
        print(f"  Failed: {len(failed_files)}")

        if failed_files:
            print(f"\nFailed files:")
            for file, error in failed_files:
                print(f"  - {file}: {error}")

        return pdf_files


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Convert PowerPoint presentations (.ppt, .pptx) to PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single file
  python ppt_to_pdf.py presentation.ppt

  # Convert with custom output name
  python ppt_to_pdf.py presentation.pptx -o output.pdf

  # Convert all files in directory
  python ppt_to_pdf.py ./presentations -b

  # Convert recursively
  python ppt_to_pdf.py ./presentations -b -r -o ./pdfs

Supported formats: .ppt, .pptx, .pptm, .pps, .ppsx
        """
    )

    parser.add_argument(
        "input",
        help="Input PowerPoint file or directory"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output PDF file or directory"
    )

    parser.add_argument(
        "-b", "--batch",
        action="store_true",
        help="Batch mode: convert all PowerPoint files in input directory"
    )

    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Process subdirectories recursively (requires -b)"
    )

    args = parser.parse_args()

    try:
        converter = PowerPointConverter()

        if args.batch:
            pdf_files = converter.convert_batch(
                args.input,
                args.output,
                args.recursive
            )
            if pdf_files:
                print(f"\n[OK] Created {len(pdf_files)} PDF file(s)")
        else:
            pdf_path = converter.convert_file(args.input, args.output)
            print(f"[OK] Created: {pdf_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
