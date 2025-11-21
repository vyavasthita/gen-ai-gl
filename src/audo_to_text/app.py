"""Legacy entrypoint forwarding to CLI.

Prefer running the CLI directly:
    python src/audo_to_text/cli/cli.py --audio path/to/file.wav --model tiny

This file is kept as a convenience; it invokes the same logic with
default arguments.
"""
from .cli.cli import main  # Adjusted import to package-relative path

if __name__ == "__main__":  # pragma: no cover
    main()