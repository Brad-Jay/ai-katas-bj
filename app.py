import os
import streamlit as st
from openai import OpenAI

# Initialize the OpenAI client and assistant
client = OpenAI()
assistant = client.beta.assistants.retrieve(assistant_id=os.environ['OPENAI_ASS_KEY'])

# Initialize the session state
if 'thread_id' not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state['thread_id'] = thread.id

if 'seen_message_ids' not in st.session_state:
    st.session_state['seen_message_ids'] = set()

if 'conversation_history' not in st.session_state:
    st.session_state['conversation_history'] = []

def get_latest_response(thread_id):
    """Retrieve and return the latest responses from the assistant."""
    messages_iterable = client.beta.threads.messages.list(thread_id=thread_id)
    messages = list(messages_iterable)

    response_texts = []
    for message in messages:
        if message.id not in st.session_state['seen_message_ids'] and message.role == "assistant":
            if message.content and hasattr(message.content[0], 'text'):
                response_text = message.content[0].text.value
                response_texts.append(response_text)
                st.session_state['seen_message_ids'].add(message.id)
    
    return response_texts

def send_initial_greeting():
    """Send the initial greeting from the assistant."""
    run = client.beta.threads.runs.create_and_poll(
        thread_id=st.session_state['thread_id'],
        assistant_id=assistant.id,
    )
    if run.status == 'completed':
        responses = get_latest_response(st.session_state['thread_id'])
        for response in responses:
            st.session_state['conversation_history'].append(("Assistant", response))

# Run the initial greeting only once
if 'initial_greeting_sent' not in st.session_state:
    send_initial_greeting()
    st.session_state['initial_greeting_sent'] = True

# UI rendering
st.title("OpenAI Chatbot with Streamlit")

# Use a placeholder for the chat history
chat_container = st.container()

with chat_container:
    st.markdown("### Chat History")
    for role, message in st.session_state['conversation_history']:
        formatted_role = "Assistant" if role == "Assistant" else "You"
        st.markdown(f"**{formatted_role}:** {message}")

# Input box and button
user_input = st.text_input("Enter your message here:")

if st.button("Send") and user_input.strip():
    # Add the user input to the conversation history
    st.session_state['conversation_history'].append(("You", user_input))

    # Create user message
    client.beta.threads.messages.create(
        thread_id=st.session_state['thread_id'],
        role="user",
        content=user_input
    )

    # Process the user's input and retrieve the assistant's response
    run = client.beta.threads.runs.create_and_poll(
        thread_id=st.session_state['thread_id'],
        assistant_id=assistant.id,
    )

    if run.status == 'completed':
        responses = get_latest_response(st.session_state['thread_id'])
        for response in responses:
            st.session_state['conversation_history'].append(("Assistant", response))

    # Only update the chat container to show new messages
    with chat_container:
        st.markdown("### Chat History")
        for role, message in st.session_state['conversation_history']:
            formatted_role = "Assistant" if role == "Assistant" else "You"
            st.markdown(f"**{formatted_role}:** {message}")
