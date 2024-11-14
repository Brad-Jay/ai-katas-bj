import openai
import streamlit as st

st.title("IAS is Winner~~~~")

openai.api_key = st.secrets["OPENAI_API_KEY"]

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"  # or "gpt-3.5-turbo" if using GPT-3.5

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Hey, I am your AI assistant. How can I help you?"}]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
prompt = st.chat_input("What is up?")
if prompt:
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate a response
    try:
        response = openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=st.session_state.messages
        )
        assistant_reply = response['choices'][0]['message']['content']

        with st.chat_message("assistant"):
            st.markdown(assistant_reply)

        # Add assistant's reply to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    except Exception as e:
        st.error(f"Error: {e}")
