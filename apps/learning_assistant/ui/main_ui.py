import streamlit as st

class LearningAssistantUI:
    def __init__(self):
        if "la_chat_history" not in st.session_state:
            st.session_state["la_chat_history"] = []
        if "la_selected_language" not in st.session_state:
            st.session_state["la_selected_language"] = None

    def display(self):
        st.markdown("""
            <div style='text-align: center;'>
                <h3 style='display: inline-block; margin-bottom: 0px;'>Language Learning Assistant</h3><br>
                <hr style='border:1px solid #DDD; width: 340px; margin: 8px auto 20px auto;'>
            </div>
        """, unsafe_allow_html=True)
        # --- Chat Bubble CSS ---
        st.markdown("""
        <style>
        .chat-container { display: flex; flex-direction: column; gap: 10px; }
        .user-bubble { background-color: #0084ff; color: white; padding: 12px; border-radius: 18px; max-width: 60%; align-self: flex-end; font-size: 16px; }
        .ai-bubble { background-color: #e5e5ea; color: black; padding: 12px; border-radius: 18px; max-width: 60%; align-self: flex-start; font-size: 16px; }
        </style>
        """, unsafe_allow_html=True)
        self.select_language()
        if st.session_state["la_selected_language"]:
            self.chat_bubble_ui()
        else:
            st.info("Please select a language to start your learning journey.")

    def select_language(self):
        languages = ["Hindi", "Spanish", "French", "Mandarin", "German"]
        selected = st.selectbox("Select your target language:", languages, key="la_language_select")
        st.session_state["la_selected_language"] = selected

    def chat_bubble_ui(self):
        if "la_messages" not in st.session_state:
            st.session_state["la_messages"] = []
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        for msg in st.session_state["la_messages"]:
            if msg["role"] == "user":
                st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='ai-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        user_input = st.text_input("Type your message and press Enter:", key="la_user_input", on_change=self.on_enter)

    def on_enter(self):
        user_input = st.session_state.get("la_user_input", "").strip()
        if user_input:
            st.session_state["la_messages"].append({"role": "user", "content": user_input})
            st.session_state["la_messages"].append({"role": "assistant", "content": "(AI response will appear here in future version.)"})
            st.session_state["la_user_input"] = ""
