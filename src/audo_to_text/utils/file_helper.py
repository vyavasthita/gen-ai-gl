from pathlib import Path


class FileHelper:
    """Utility class for file and directory operations."""
    def __init__(self, base_dir: str = "transcriptions"):
        self.base_dir = Path(base_dir)
        self.ensure_base_dir()

    def ensure_base_dir(self):
        """Create base directory if it doesn't exist."""
        self.base_dir.mkdir(exist_ok=True)

    def write_text_file(self, filename: str, text: str) -> Path:
        """Write text to a file in the base directory."""
        file_path = self.base_dir / filename
        file_path.write_text(text, encoding="utf-8")
        return file_path

    def get_file_path(self, filename: str) -> Path:
        """Get full path for a file in the base directory."""
        return self.base_dir / filename
