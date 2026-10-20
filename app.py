# import streamlit as st
# from openai import APIError
# from ai_client import create_history, get_study_response


# # -----------------------------------
# # 1. Page configuration
# # -----------------------------------

# st.set_page_config(
#     page_title="AI Study Assistant",
#     page_icon="📚",
#     layout="centered",
# )

# st.title("AI Study Assistant")
# st.caption(
#     "Your learning companion for explanations, summaries, "
#     "and practice questions."
# )


# # -----------------------------------
# # 2. Initialize conversation state
# # -----------------------------------

# if "messages" not in st.session_state:
#     st.session_state.messages = create_history()


# # -----------------------------------
# # 3. Sidebar
# # -----------------------------------

# with st.sidebar:
#     st.header("Study Assistant")
#     st.write("What would you like to learn today?")

#     st.divider()

#     st.subheader("Available features")
#     st.write("- Explain concepts")
#     st.write("- Summarize text")
#     st.write("- Generate practice questions")

#     if st.button("New conversation", use_container_width=True):
#         st.session_state.messages = create_history()
#         st.rerun()


# # -----------------------------------
# # 4. Display previous chat messages
# # -----------------------------------

# for message in st.session_state.messages:
#     if message["role"] == "system":
#         continue

#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])


# # -----------------------------------
# # 5. Accept a new question
# # -----------------------------------

# prompt = st.chat_input("Ask a study question...")

# if prompt:
#     # Display the user's question immediately.
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # Prepare conversation history for the API.
#     next_messages = st.session_state.messages + [
#         {"role": "user", "content": prompt}
#     ]

#     try:
#         with st.chat_message("assistant"):
#             with st.spinner("Thinking..."):
#                 answer = get_study_response(next_messages)

#             st.markdown(answer)

#         # Save history only after a successful response.
#         st.session_state.messages = next_messages + [
#             {"role": "assistant", "content": answer}
#         ]

#     except (APIError, ValueError) as error:
#         st.error(
#             "Could not get an answer. Check your API configuration "
#             "and connection, then try again."
#         )
#         print(f"AI API error: {error}")
#         # to run write command in terminal :"python -m streamlit run app.py"


#meta code
import streamlit as st
import json
import os
from datetime import datetime
from openai import APIError
from ai_client import create_history, get_study_response

# -----------------------------------
# 1. Page configuration
# -----------------------------------
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="centered",
)

# ---- NEW: File to store chats permanently ----
CHAT_FILE = "chat_history.json"

def load_chats():
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_chats():
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.all_chats, f, indent=2, ensure_ascii=False)

# -----------------------------------
# 2. Initialize conversation state
# -----------------------------------
if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_chats()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "messages" not in st.session_state:
    st.session_state.messages = create_history()

# -----------------------------------
# 3. Sidebar - UPDATED FOR YOUR FEATURE
# -----------------------------------
with st.sidebar:
    st.header("Study Assistant")
    st.write("What would you like to learn today?")

    if st.button("➕ New conversation", use_container_width=True, type="primary"):
        st.session_state.messages = create_history()
        st.session_state.current_chat_id = None
        st.rerun()

    st.divider()

    st.subheader("Previous Chats")
    if not st.session_state.all_chats:
        st.caption("No previous chats yet.")
    else:
        # Show newest first
        for chat in reversed(st.session_state.all_chats):
            title = chat["title"]
            short_title = title[:35] + "..." if len(title) > 35 else title
            # Button for each chat tab
            if st.button(short_title, key=chat["id"], use_container_width=True):
                st.session_state.messages = chat["messages"]
                st.session_state.current_chat_id = chat["id"]
                st.rerun()

    st.divider()
    st.subheader("Available features")
    st.write("- Explain concepts")
    st.write("- Summarize text")
    st.write("- Generate practice questions")

# -----------------------------------
# 4. Display previous chat messages
# -----------------------------------
st.title("AI Study Assistant")
st.caption("Your learning companion for explanations, summaries, and practice questions.")

for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------
# 5. Accept a new question - UPDATED SAVING LOGIC
# -----------------------------------
prompt = st.chat_input("Ask a study question...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    next_messages = st.session_state.messages + [
        {"role": "user", "content": prompt}
    ]

    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = get_study_response(next_messages)
            st.markdown(answer)

        st.session_state.messages = next_messages + [
            {"role": "assistant", "content": answer}
        ]

        # ---- NEW: Save to sidebar history with title ----
        if st.session_state.current_chat_id is None:
            # Create new chat entry, title = user's question
            new_id = str(datetime.now().timestamp())
            new_chat = {
                "id": new_id,
                "title": prompt,
                "messages": st.session_state.messages,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.all_chats.append(new_chat)
            st.session_state.current_chat_id = new_id
        else:
            # Update existing chat
            for c in st.session_state.all_chats:
                if c["id"] == st.session_state.current_chat_id:
                    c["messages"] = st.session_state.messages
                    break
        
        save_chats()

    except (APIError, ValueError) as error:
        st.error("Could not get an answer. Check your API configuration and connection, then try again.")
        print(f"AI API error: {error}")