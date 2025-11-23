import os
from pathlib import Path

class FileHelper:
    """
    Generic file helper for resource management across apps.
    Handles creation of resource directories and file operations.
    """
    def __init__(self, app_name: str, resource_root: str = "/tmp/resources"):
        self.app_name = app_name
        self.resource_root = Path(resource_root)
        self.app_resource_dir = self.resource_root / app_name
        self.app_resource_dir.mkdir(parents=True, exist_ok=True)

    def get_app_resource_dir(self) -> Path:
        """Return the app-specific resource directory."""
        return self.app_resource_dir

    def get_subdir(self, subdir: str) -> Path:
        """Return (and create if needed) a subdirectory under the app resource dir."""
        subdir_path = self.app_resource_dir / subdir
        subdir_path.mkdir(parents=True, exist_ok=True)
        return subdir_path

    def write_text_file(self, subdir: str, filename: str, text: str) -> Path:
        """Write text to a file in a subdirectory and return the file path."""
        target_dir = self.get_subdir(subdir)
        file_path = target_dir / filename
        file_path.write_text(text, encoding="utf-8")
        return file_path

    def list_files(self, subdir: str) -> list:
        """List all files in a subdirectory."""
        target_dir = self.get_subdir(subdir)
        return [f for f in target_dir.iterdir() if f.is_file()]
