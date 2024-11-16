import streamlit as st
from openai import OpenAI
import os

# Initialize OpenAI client
client = OpenAI()
assistant = client.beta.assistants.retrieve(assistant_id=os.environ['OPENAI_ASS_KEY'])

# Create a thread (Conversation instance)
thread = client.beta.threads.create()

# Set to track processed message IDs
seen_message_ids = set()

def get_latest_response(thread_id):
    # Retrieve messages and convert to list
    messages_iterable = client.beta.threads.messages.list(thread_id=thread_id)
    messages = list(messages_iterable)

    responses = []
    for message in messages:
        # Only get new assistant messages
        if message.id not in seen_message_ids and message.role == "assistant":
            # Check for 'text' attribute in content
            if message.content and hasattr(message.content[0], 'text'):
                responses.append(message.content[0].text.value)
            
            # Add the message ID to the seen set
            seen_message_ids.add(message.id)
    return responses

# Start the assistant
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
)

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Check if the initial run was successful and get setup response
if run.status == 'completed' and not st.session_state['chat_history']:
    initial_responses = get_latest_response(thread.id)
    for response in initial_responses:
        st.session_state['chat_history'].append({'role': 'assistant', 'content': response})

# Streamlit app interface
st.title("Chatbot Interface")

# Display chat history
chat_container = st.container()
with chat_container:
    for chat in st.session_state['chat_history']:
        if chat['role'] == 'user':
            st.markdown(f"**You:** {chat['content']}")
        else:
            st.markdown(f"**Assistant:** {chat['content']}")

# Create a placeholder for the input box
input_placeholder = st.empty()

# Input box for user input
user_input = input_placeholder.text_input("Enter your message:", key="input")

if user_input:
    # Add user input to chat history
    st.session_state['chat_history'].append({'role': 'user', 'content': user_input})

    # Create a new message in the thread with the user's input
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )

    # Poll the thread to process the user's input
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    # Get only the new assistant responses
    if run.status == 'completed':
        responses = get_latest_response(thread.id)
        for response in responses:
            st.session_state['chat_history'].append({'role': 'assistant', 'content': response})

    # Clear the input box after submission
    input_placeholder.text_input("Enter your message:", value="", key="new_input")
