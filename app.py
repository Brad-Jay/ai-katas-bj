import os
import streamlit as st
from openai import OpenAI

# Initialize the OpenAI client and assistant
client = OpenAI()
assistant = client.beta.assistants.retrieve(assistant_id=os.environ['OPENAI_ASS_KEY'])

# Initialize the session state for the thread and messages
if 'thread_id' not in st.session_state:
    # Create a new thread if it doesn't exist
    thread = client.beta.threads.create()
    st.session_state['thread_id'] = thread.id

# Initialize the chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "Assistant", "content": "Chat is loading....."}]

# Function to get the latest assistant's response
def get_latest_response(thread_id):
    messages_iterable = client.beta.threads.messages.list(thread_id=thread_id)
    messages = list(messages_iterable)
    
    responses = []
    for message in messages:
        if message.role == "assistant" and message.content and hasattr(message.content[0], 'text'):
            responses.append(message.content[0].text.value)
    
    return responses

# Function to send the initial greeting from the assistant
def send_initial_greeting():
    run = client.beta.threads.runs.create_and_poll(
        thread_id=st.session_state['thread_id'],
        assistant_id=assistant.id,
    )
    if run.status == 'completed':
        responses = get_latest_response(st.session_state['thread_id'])
        for response in responses:
            st.session_state['messages'].append({"role": "Assistant", "content": response})

# Run the initial greeting only once
if 'initial_greeting_sent' not in st.session_state:
    send_initial_greeting()
    st.session_state['initial_greeting_sent'] = True

# UI rendering
st.title("OpenAI Chatbot with Streamlit")

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "Assistant":
            st.image("assistant_image.png", width=50)
        else:
            st.image("user_image.png", width=50)
        st.markdown(message["content"])

# Input box and send button
user_input = st.text_input("Enter your message here:")

if st.button("Send") and user_input.strip():
    # Add the user input to the conversation history
    st.session_state['messages'].append({"role": "You", "content": user_input})

    # Send the user message to OpenAI
    client.beta.threads.messages.create(
        thread_id=st.session_state['thread_id'],
        role="user",
        content=user_input
    )

    # Process the assistant's response after user input
    run = client.beta.threads.runs.create_and_poll(
        thread_id=st.session_state['thread_id'],
        assistant_id=assistant.id,
    )
    
    if run.status == 'completed':
        responses = get_latest_response(st.session_state['thread_id'])
        for response in responses:
            st.session_state['messages'].append({"role": "Assistant", "content": response})

    # Update the chat with the latest messages
    for message in st.session_state['messages']:
        with st.chat_message(message["role"]):
            if message["role"] == "Assistant":
                st.image("assistant_image.png", width=50)
            else:
                st.image("user_image.png", width=50)
            st.markdown(message["content"])
