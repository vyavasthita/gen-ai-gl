"""
Export and download UI utilities for transcription app.
Provides PDF, SRT, and text download via dropdown for Streamlit UI.
"""

from fpdf import FPDF
import streamlit as st


__all__ = ["ExportUI", "export_dropdown"]


def export_dropdown(text: str):
    """Backward-compatible function for export_dropdown. Uses ExportUI class."""
    ExportUI(text).export_dropdown()


class ExportUI:
    """Class-based export and download UI utilities for transcription app."""
    def __init__(self, text: str):
        self.text = text

    def show_pdf_download(self):
        """Render a download button for PDF export."""
        pdf_bytes = self.generate_pdf_bytes()
        st.download_button("Download PDF", data=pdf_bytes, file_name="transcription.pdf", mime="application/pdf")

    def show_srt_download(self):
        """Render a download button for SRT export."""
        srt_text = self.transcription_to_srt()
        st.download_button("Download SRT", data=srt_text, file_name="transcription.srt", mime="text/plain")

    def show_text_download(self):
        """Render a download button for plain text export."""
        st.download_button("Download Text", data=self.text, file_name="transcription.txt", mime="text/plain")

    def select_export_format(self) -> str:
        """Show dropdown for download format and return selected value."""
        return st.selectbox(
            "Choose download format:",
            ["PDF", "SRT", "Text"],
            index=0,
            key="export_format_select"
        )

    def export_dropdown(self):
        """Show download button for selected format."""
        export_format = self.select_export_format()
        
        if export_format == "PDF":
            self.show_pdf_download()
        elif export_format == "SRT":
            self.show_srt_download()
        else:
            self.show_text_download()

    def generate_pdf_bytes(self) -> bytes:
        """Generate PDF bytes from transcription text."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in self.text.splitlines():
            pdf.cell(200, 10, txt=line, ln=1)
        return pdf.output(dest="S").encode("utf-8")

    def transcription_to_srt(self) -> str:
        """Convert plain text transcription to minimal SRT format."""
        # Minimal SRT: one block, no timestamps
        return "1\n00:00:00,000 --> 00:00:10,000\n" + self.text + "\n"
