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
        .chat-box { display: flex; flex-direction: column; gap: 12px; padding-top: 10px; }
        .user-bubble { background-color: #0084ff; color: white; padding: 12px 16px; border-radius: 18px; max-width: 60%; align-self: flex-end; font-size: 16px; }
        .ai-bubble { background-color: #e5e5ea; color: black; padding: 12px 16px; border-radius: 18px; max-width: 60%; align-self: flex-start; font-size: 16px; }
        </style>
        """, unsafe_allow_html=True)
        self.sidebar_language_settings()
        self.chat_bubble_ui()

    def sidebar_language_settings(self):
        st.sidebar.title("🌐 Language Settings")
        languages = ["Hindi", "Spanish", "French", "Mandarin", "German", "English", "Japanese", "Korean"]
        selected = st.sidebar.selectbox("Select Language", languages, key="la_language_select")
        level = st.sidebar.selectbox("Proficiency Level", ["Beginner", "Intermediate", "Advanced"], key="la_level_select")
        st.sidebar.info(f"🌍 You are learning **{selected}** at **{level}** level.")
        st.session_state["la_selected_language"] = selected
        st.session_state["la_selected_level"] = level

    def chat_bubble_ui(self):
        if "la_messages" not in st.session_state:
            st.session_state["la_messages"] = [
                {"role": "assistant", "content": f"Hello! Let's practice **{st.session_state.get('la_selected_language', 'your language')}**. How can I help today?"}
            ]
        st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
        for msg in st.session_state["la_messages"]:
            if msg["role"] == "assistant":
                st.markdown(f"<div class='ai-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        user_input = st.text_input("Type your message and press Enter:", key="la_user_input", on_change=self.on_enter)

    def on_enter(self):
        user_input = st.session_state.get("la_user_input", "").strip()
        if user_input:
            st.session_state["la_messages"].append({"role": "user", "content": user_input})
            st.session_state["la_messages"].append({"role": "assistant", "content": f"I see! Here's how to express that in {st.session_state.get('la_selected_language', 'your language')}..."})
            st.session_state["la_user_input"] = ""
            st.experimental_rerun()
