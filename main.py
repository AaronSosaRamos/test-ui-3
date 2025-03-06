import streamlit as st
import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ENDPOINT_URL = os.getenv("ENDPOINT_URL")

def main():
    st.set_page_config(page_title="Multi-Agent Subatomic Chatbot", layout="wide")
    
    # Custom styling
    st.markdown(
        """
        <style>
        .chat-container {
            max-width: 800px;
            margin: auto;
        }
        .stButton > button {
            width: 100%;
            padding: 10px;
            border-radius: 10px;
            font-size: 16px;
        }
        .stChatMessage {
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("""
    <h1 style='text-align: center;'>🤖 Multi-Agent Subatomic Chatbot</h1>
    <p style='text-align: center;'>An intelligent AI-powered assistant for seamless conversations.</p>
    <hr>
    """, unsafe_allow_html=True)
    
    # Initialize chat history if not present
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        # Predefined assistant message (NOT SENT TO API)
        st.session_state.chat_history.append({"role": "assistant", "content": "Hello! How can I assist you today?"})

    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # User input
    query = st.chat_input("Type your message")

    if query:
        # Append user query to chat history
        st.session_state.chat_history.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.spinner("Assistant is typing..."):

            # Send the first user query directly to the API
            payload = {"query": query}

            # If conversation_id and user_id exist, include them
            if "conversation_id" in st.session_state and "user_id" in st.session_state:
                payload["conversation_id"] = st.session_state.conversation_id
                payload["user_id"] = st.session_state.user_id

            try:
                response = requests.post(f"{ENDPOINT_URL}/api/rag-agent/chatbot", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    assistant_response = data.get("response", "No response")

                    # Store conversation_id and user_id if returned (only on the first API response)
                    if "conversation_id" not in st.session_state and "user_id" not in st.session_state:
                        st.session_state.conversation_id = data.get("conversation_id")
                        st.session_state.user_id = data.get("user_id")
                else:
                    assistant_response = "An error occurred while processing your request."
            except Exception:
                assistant_response = "An error occurred while processing your request."

        # Streaming response simulation
        def word_by_word(text):
            words = text.split()
            for i, word in enumerate(words):
                yield word + (" " if i < len(words)-1 else "")
                time.sleep(0.1)  # Simulate typing delay

        with st.chat_message("assistant"):
            streamed_text = st.write_stream(word_by_word(assistant_response))
        st.session_state.chat_history.append({"role": "assistant", "content": streamed_text})

    # Clear conversation button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Conversation"):
            st.session_state.chat_history = []
            st.session_state.pop("conversation_id", None)
            st.session_state.pop("user_id", None)
            st.rerun()
    with col2:
        if st.button("Back to Dashboard"):
            print("Hello world!")

if __name__ == "__main__":
    main()
