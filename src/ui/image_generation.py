import streamlit as st
import requests
import base64
import os

st.set_page_config(page_title="Text → Image Demo", page_icon="🎨")

st.title("🎨 Text to Image using OpenAI (DALL·E / gpt-image-1)")

st.write("Enter a text prompt and generate an image using OpenAI's Image API.")

# --- Read API KEY from environment ---
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("Environment variable OPENAI_API_KEY not found. Please export it before running the app.")
    st.stop()

# --- User prompt ---
prompt = st.text_area("Enter your prompt")

if st.button("Generate Image"):
    if not prompt.strip():
        st.error("Please enter a valid prompt.")
    else:
        with st.spinner("Generating image..."):

            # ❗ FIXED: correct endpoint
            url = "https://api.openai.com/v1/images/generations"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            data = {
                "model": "gpt-image-1",
                "prompt": prompt,
                "size": "1024x1024"
            }

            try:
                response = requests.post(url, json=data, headers=headers)

                # Debug output (optional)
                print("RAW RESPONSE TEXT:", response.text)

                result = response.json()

                if "data" in result:
                    image_base64 = result["data"][0]["b64_json"]
                    image_bytes = base64.b64decode(image_base64)

                    st.image(image_bytes, caption="Generated Image", use_column_width=True)
                else:
                    st.error(f"API Error: {result}")

            except Exception as e:
                st.error(f"Request failed: {e}")
