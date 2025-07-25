import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Gemini VEO3 Assistant",
    page_icon="🎬",
    layout="wide"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def load_system_prompt():
    """Load the system prompt from the markdown file"""
    try:
        with open('veo3-assistant-system-prompt.md', 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        st.error("System prompt file not found!")
        return "You are a helpful assistant."

def initialize_gemini():
    """Initialize Gemini with API key from .env"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        st.error("GEMINI_API_KEY not found in .env file!")
        st.info("Please create a .env file with your Gemini API key: GEMINI_API_KEY=your_key_here")
        return None
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        # Test the connection
        response = model.generate_content("Hello")
        return model
    except Exception as e:
        st.error(f"Failed to initialize Gemini: {str(e)}")
        return None

def chat_with_gemini(model, system_prompt, user_message):
    """Send message to Gemini and get response"""
    try:
        # Combine system prompt and user message
        full_prompt = f"{system_prompt}\n\nUser: {user_message}\n\nAssistant:"
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    st.title("🎬 Gemini VEO3 Assistant")
    st.markdown("---")
    
    # Load system prompt
    system_prompt = load_system_prompt()
    
    # Initialize Gemini
    model = initialize_gemini()
    
    if model is None:
        st.stop()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.info("Using VEO3 Assistant System Prompt")
        
        # Model selection
        model_name = st.selectbox(
            "Model",
            ["gemini-2.5-flash", "gemini-1.5-pro"],
            index=0
        )
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Main chat interface
    st.header("💬 Chat Interface")
    
    # Chat input
    user_input = st.text_area(
        "Enter your message:",
        height=100,
        placeholder="Create a prompt for a mysterious forest scene..."
    )
    
    # Send button
    if st.button("🚀 Send", type="primary"):
        if user_input.strip():
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Get response from Gemini
            with st.spinner("Generating response..."):
                response = chat_with_gemini(model, system_prompt, user_input)
            
            # Add assistant response to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })
            
            st.rerun()
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("---")
        st.header("📝 Chat History")
        
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
    


if __name__ == "__main__":
    main() 
