import os
import streamlit as st
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI()
assistant = client.beta.assistants.retrieve(assistant_id=os.environ['OPENAI_ASS_KEY'])

# Create a thread (Conversation instance)
thread = client.beta.threads.create()

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

# Streamlit UI
st.title("OpenAI Chatbot with Streamlit")

# Text input for user query
user_input = st.text_input("Enter your message here:", "")

# Button to send user query
if st.button("Send"):
    if user_input:
        # Display user input
        st.write(f"**You:** {user_input}")
        
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

        # Get and display the new assistant responses
        if run.status == 'completed':
            responses = get_latest_response(thread.id)
            for response in responses:
                st.write(f"**Assistant:** {response}")
        else:
            st.write("The assistant is still thinking...")

# Keep the chat history visible
st.write("## Chat History")

# Function to display chat history
def display_chat_history():
    messages_iterable = client.beta.threads.messages.list(thread_id=thread.id)
    messages = list(messages_iterable)

    for message in messages:
        role = "You" if message.role == "user" else "Assistant"
        if message.content and hasattr(message.content[0], 'text'):
            st.write(f"**{role}:** {message.content[0].text.value}")

# Call the function to display the chat history
display_chat_history()
