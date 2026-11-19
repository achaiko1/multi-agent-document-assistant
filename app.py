import os
import re
from dotenv import load_dotenv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from src.assistant import DocumentAssistant

load_dotenv()
import streamlit as st

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except (KeyError, FileNotFoundError):
        api_key = None

if not api_key:
    st.error("OPENAI_API_KEY is missing. Check your .env file.")
    st.stop()

if "assistant" not in st.session_state:
    
    st.session_state.assistant = DocumentAssistant(
        openai_api_key=api_key,
        model_name=os.getenv("MODEL_NAME", "openai/gpt-oss-20b"),
        temperature=0.1,
        load_samples=False
    )


    st.session_state.assistant.start_session("web_user")

st.set_page_config(
    page_title="Document Intelligence",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Multi-Agent Document Intelligence")

st.write(
    "Upload documents, ask questions, generate summaries, "
    "and perform calculations using specialized AI agents."
)

with st.sidebar:
    st.header("Documents")
    if "upload_success" in st.session_state:
        st.success(st.session_state.pop("upload_success"))
    st.subheader("Uploaded Documents")

    documents = st.session_state.assistant.retriever.documents

    
    if documents:
        for doc_id, document in list(documents.items()):
            col1, col2 = st.columns([4, 1])

            with col1:
                st.write(f"📄 {document.title}")
                st.caption(f"ID: {doc_id}")

            with col2:
                if st.button("🗑️", key=f"delete_{doc_id}", help="Remove document"):
                    del st.session_state.assistant.retriever.documents[doc_id]
                    st.rerun()

    else:
        st.caption("No documents uploaded yet.")

    st.divider()

    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"]
    )

    
    if uploaded_file is not None:
        import tempfile

        if st.button("Process PDF"):
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir) / Path(uploaded_file.name).name
                temp_path.write_bytes(uploaded_file.getbuffer())

                try:
                    doc_id = st.session_state.assistant.upload_pdf(str(temp_path))
                    st.session_state.upload_success = f"Document registered: {doc_id}"
                    st.rerun()
                except Exception as e:
                    st.error(f"Upload failed: {e}")



st.subheader("AI Assistant")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# Display previous messages
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

        if message.get("intent"):
            st.caption(f"Agent: {message['intent']}")

        if message.get("tools"):
            st.caption(f"Tools: {', '.join(message['tools'])}")



# Limit AI requests per browser session
MAX_REQUESTS = 20

if "request_count" not in st.session_state:
    st.session_state.request_count = 0

# Handle new user messages
user_input = st.chat_input(
    "Ask a question about your documents...",
    disabled=st.session_state.request_count >= MAX_REQUESTS
)


if st.session_state.request_count >= MAX_REQUESTS:
    st.warning(f"You've reached the {MAX_REQUESTS}-message limit for this demo.")

if user_input:
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing documents..."):
            st.session_state.request_count += 1
            result = st.session_state.assistant.process_message(user_input)

        if result["success"]:
            
            response = result.get("response") or "No response generated."

            # Remove leaked internal tool-call syntax
            response = re.sub(
                r"【assistant\s+to=[^】]*】",
                "",
                response
            )

            # Convert tool citations into readable source references
            response = re.sub(
                r"【(?:document_search|document_reader):([^】]+)】",
                r"(Source: \1)",
                response
            )

            intent = result.get("intent")
            tools = result.get("tools_used", [])

            st.write(response)

            if intent:
                st.caption(f"Agent: {intent['intent_type']}")

            if tools:
                st.caption(f"Tools: {', '.join(tools)}")

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "intent": intent["intent_type"] if intent else None,
                "tools": tools
            })
        else:
            st.error(result.get("error", "Unknown error"))

