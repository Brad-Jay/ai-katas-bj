import os
import streamlit as st
from openai import OpenAI

# Initialize the OpenAI client and assistant
client = OpenAI()
assistant = client.beta.assistants.retrieve(assistant_id=os.environ['OPENAI_ASS_KEY'])

# Create a persistent thread only once when the app starts
if 'thread_id' not in st.session_state:
    # Create a thread (Conversation instance) only once
    thread = client.beta.threads.create()
    st.session_state['thread_id'] = thread.id

# Set to track processed message IDs
seen_message_ids = set()

def get_latest_response(thread_id):
    """Retrieve and display the latest responses from the assistant."""
    messages_iterable = client.beta.threads.messages.list(thread_id=thread_id)
    messages = list(messages_iterable)

    response_texts = []
    for message in messages:
        if message.id not in seen_message_ids and message.role == "assistant":
            if message.content and hasattr(message.content[0], 'text'):
                response_texts.append(message.content[0].text.value)
            seen_message_ids.add(message.id)
    
    return response_texts

# Initialize Streamlit UI
st.title("OpenAI Chatbot with Streamlit")

# Initialize conversation history in Streamlit's session state
if 'conversation_history' not in st.session_state:
    st.session_state['conversation_history'] = []

# Start the assistant and send an initial greeting if it hasn't been sent yet
if 'initial_greeting_sent' not in st.session_state:
    # Run the assistant's initial greeting message
    run = client.beta.threads.runs.create_and_poll(
        thread_id=st.session_state['thread_id'],
        assistant_id=assistant.id,
    )

    # If the run is successful, capture the initial greeting
    if run.status == 'completed':
        initial_responses = get_latest_response(st.session_state['thread_id'])
        for response in initial_responses:
            st.session_state['conversation_history'].append(("Assistant", response))
            st.write(f"**Assistant:** {response}")

    st.session_state['initial_greeting_sent'] = True

# Display chat history if there's any
st.write("## Chat History")
for role, message in st.session_state['conversation_history']:
    st.write(f"**{role}:** {message}")

# Text input for user query
user_input = st.text_input("Enter your message here:", "")

# Button to send user query
if st.button("Send") and user_input:
    # Display user input
    st.write(f"**You:** {user_input}")

    # Create a new message in the persistent thread with the user's input
    client.beta.threads.messages.create(
        thread_id=st.session_state['thread_id'],
        role="user",
        content=user_input
    )

    # Poll the thread to process the user's input
    run = client.beta.threads.runs.create_and_poll(
        thread_id=st.session_state['thread_id'],
        assistant_id=assistant.id,
    )

    # Get and display the new assistant responses
    if run.status == 'completed':
        responses = get_latest_response(st.session_state['thread_id'])
        for response in responses:
            st.session_state['conversation_history'].append(("Assistant", response))
            st.write(f"**Assistant:** {response}")

    # Add the user input to the conversation history
    st.session_state['conversation_history'].append(("You", user_input))
