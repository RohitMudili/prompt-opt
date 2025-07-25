# Gemini VEO3 Assistant Setup Guide

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Gemini API Key** from Google AI Studio

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a `.env` file** in the project root:
   ```
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

3. **Get your Gemini API Key:**
   - Go to [Google AI Studio](https://aistudio.google.com/)
   - Sign in with your Google account
   - Create a new API key
   - Copy the key and paste it in your `.env` file

## Running the Application

1. **Start the Streamlit app:**
   ```bash
   streamlit run gemini_streamlit_interface.py
   ```

2. **Open your browser** and go to the URL shown in the terminal (usually `http://localhost:8501`)

## Features

- **Chat Interface**: Send messages to the VEO3 Assistant
- **System Prompt**: Uses the comprehensive VEO3 system prompt from `veo3-assistant-system-prompt.md`
- **Chat History**: View your conversation history
- **Quick Examples**: Pre-built example prompts to get started
- **Model Selection**: Choose between Gemini 1.5 Flash and Pro models

## Usage

1. Enter your prompt in the text area
2. Click "Send" to get a response from the VEO3 Assistant
3. Use the sidebar to clear chat history or change models
4. Try the quick examples to see how the assistant works

## Example Prompts

- "Create a prompt for a mysterious forest scene"
- "Generate a cinematic prompt for a city at night"
- "Write a prompt for a peaceful beach sunset"
- "Create a prompt for a futuristic robot in a laboratory"
- "Generate a prompt for a magical library with floating books"

## Troubleshooting

- **API Key Error**: Make sure your `.env` file contains the correct Gemini API key
- **Model Error**: Try switching between Flash and Pro models in the sidebar
- **File Not Found**: Ensure `veo3-assistant-system-prompt.md` is in the same directory

## Files

- `gemini_streamlit_interface.py`: Main Streamlit application
- `veo3-assistant-system-prompt.md`: System prompt for VEO3 video generation
- `requirements.txt`: Python dependencies
- `.env`: Your API keys (create this file) 