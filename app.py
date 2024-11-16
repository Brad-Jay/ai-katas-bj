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

# Streamlit app interface
st.title("Chatbot Interface")

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Display chat history
for chat in st.session_state['chat_history']:
    st.chat_message(chat['role'], chat['content'])

# Input box for user input
user_input = st.text_input("Enter something (type 'exit' to end):")

if user_input:
    if user_input.lower() == 'exit':
        st.write("Exiting the loop. Goodbye!")
    else:
        # Add user input to chat history
        st.session_state['chat_history'].append({'role': 'user', 'content': user_input})
        st.chat_message('user', user_input)

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
                st.chat_message('assistant', response)
