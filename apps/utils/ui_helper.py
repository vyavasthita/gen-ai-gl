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
        version = "0.2.0"

    st.markdown(
        f"""
        <div style='text-align: center;'>
            <strong>Author:</strong> Dilip Sharma<br>
            <strong>Version:</strong> {version}
        </div>
        <hr style='border:1px solid #DDD; margin-top: 10px; margin-bottom: 20px;'>
        """,
        unsafe_allow_html=True
    )
