import streamlit as st
import openai

# Initialize the OpenAI client (make sure your API key is set in environment variables)
openai.api_key = os.getenv('OPENAI_ASS_KEY')

# Streamlit UI
st.title("OpenAI Chatbot with Streamlit")

# Function to interact with OpenAI API
def get_openai_response(user_input, conversation_history):
    # Use the conversation history to maintain context
    messages = conversation_history + [{"role": "user", "content": user_input}]
    
    # Call the OpenAI Chat API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4" depending on your setup
        messages=messages
    )
    
    # Get the assistant's reply
    assistant_reply = response['choices'][0]['message']['content']
    
    # Update conversation history with the assistant's reply
    conversation_history.append({"role": "user", "content": user_input})
    conversation_history.append({"role": "assistant", "content": assistant_reply})
    
    return assistant_reply, conversation_history

# Initialize conversation history
if 'conversation_history' not in st.session_state:
    st.session_state['conversation_history'] = []

# Text input for user query
user_input = st.text_input("Enter your message here:", "")

# Button to send user query
if st.button("Send"):
    if user_input:
        # Display user input
        st.write(f"**You:** {user_input}")
        
        # Get OpenAI response and update conversation history
        assistant_reply, st.session_state['conversation_history'] = get_openai_response(
            user_input, st.session_state['conversation_history']
        )

        # Display the assistant's reply
        st.write(f"**Assistant:** {assistant_reply}")

# Keep the chat history visible
st.write("## Chat History")
for message in st.session_state['conversation_history']:
    role = "You" if message['role'] == "user" else "Assistant"
    st.write(f"**{role}:** {message['content']}")
