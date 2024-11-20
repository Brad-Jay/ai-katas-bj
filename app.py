from openai import OpenAI
import streamlit as st
import time
import os

client = OpenAI()
assistant_id = client.beta.assistants.retrieve(assistant_id=os.environ['OPENAI_ASS_KEY'])

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="ShopWise", page_icon=":speech_balloon:")

# When "Start Chat" button is clicked
if st.button("Start Chat"):
    st.session_state.start_chat = True
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

    # Simulate a user message (you can change the content)
    simulated_message = "Hello, how are you?"

    # Add the simulated user message to the chat interface
    #st.session_state.messages.append({"role": "user", "content": simulated_message})
    #with st.chat_message("user"):
     #   st.markdown(simulated_message)

    # Send the simulated message to the API
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=simulated_message
    )

    # Start the AI bot run
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant_id.id,
    )

    # Wait for the run to complete
    while run.status != 'completed':
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id
        )

    # Fetch and display any assistant messages in response to the simulated user message
   # messages = client.beta.threads.messages.list(
     #   thread_id=st.session_state.thread_id
    )
   # assistant_messages_for_run = [
      #  message for message in messages
       # if message.run_id == run.id and message.role == "assistant"
    ]
    #for message in assistant_messages_for_run:
      #  st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
      #  with st.chat_message("assistant"):
        #    st.markdown(message.content[0].text.value)

st.title("ShopWise Genie")

# If the chat has started
if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4-turbo"

    # Display the chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input from the chat
    if prompt := st.chat_input("Message"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Send the user input to the API
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        # Start a new run for the user input
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id.id,
        )

        # Wait for the run to complete
        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )

        # Fetch and display the assistant's response
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )
        assistant_messages_for_run = [
            message for message in messages
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
            with st.chat_message("assistant"):
                st.markdown(message.content[0].text.value)

else:
    st.write("Click 'Start Chat' to begin.")
