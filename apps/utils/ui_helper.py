import toml
import streamlit as st


def show_author_and_version():
    """
    Show author and version in bold at the top of the main UI.
    Reads version from pyproject.toml if available.
    """
    try:
        pyproject = toml.load("pyproject.toml")
        version = pyproject["project"]["version"]
    except Exception:
        # Fallback to default version if file missing or unreadable
        version = "0.1.0"

    st.markdown("**Author:** Dilip Sharma")
    st.markdown(f"**Version:** {version}")
