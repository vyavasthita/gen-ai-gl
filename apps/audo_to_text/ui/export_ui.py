

"""
export_ui.py
Export and download UI utilities for transcription app.
Provides PDF, SRT, and text download via dropdown for Streamlit UI.
"""

from fpdf import FPDF
import streamlit as st

__all__ = ["ExportUI", "export_dropdown"]

def export_pdf_button(text: str, key: str = None):
    """
    Show a single Download PDF button for exporting transcription as PDF.
    Args:
        text: Transcription text to export
        key: Unique Streamlit widget key
    """
    ExportUI(text, key=key).show_pdf_download()


class ExportUI:
    """
    Class-based export and download UI utilities for transcription app.
    Handles PDF export and download button rendering.
    """

    def __init__(self, text: str, key: str = None):
        """
        Args:
            text: Transcription text to export
            key: Unique Streamlit widget key
        """
        self.text = text
        self.key = key or "pdf_download"

    def get_pdf_lines(self) -> list:
        """
        Return lines for PDF, ensuring at least one line.
        Returns:
            List of lines for PDF
        """
        lines = self.text.splitlines()
        if not lines or all(not line.strip() for line in lines):
            return ["(No transcription)"]
        return lines

    def show_pdf_download(self):
        """
        Render a download button for PDF export in Streamlit UI.
        """
        pdf_bytes = self.generate_pdf_bytes()
        st.download_button(
            "Download PDF",
            data=pdf_bytes,
            file_name="transcription.pdf",
            mime="application/pdf",
            key=self.key
        )

    # SRT, text, and dropdown export logic can be added here if needed

    def generate_pdf_bytes(self) -> bytes:
        """
        Always generate a non-empty PDF using built-in font and ASCII fallback.
        Returns:
            PDF file bytes
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        lines = self.get_pdf_lines()
        # Fallback: replace non-ASCII with '?'
        safe_lines = []
        for line in lines:
            try:
                safe_lines.append(line.encode("ascii", "replace").decode("ascii"))
            except Exception:
                safe_lines.append("(No transcription)")
        for line in safe_lines:
            pdf.multi_cell(0, 10, txt=line)
        pdf_bytes = pdf.output(dest="S").encode("latin-1")
        return pdf_bytes

    def transcription_to_srt(self) -> str:
        """
        Convert plain text transcription to minimal SRT format.
        Returns:
            SRT formatted string
        """
        # Minimal SRT: one block, no timestamps
        return "1\n00:00:00,000 --> 00:00:10,000\n" + self.text + "\n"
