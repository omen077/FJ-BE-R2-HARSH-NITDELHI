"""
Standalone Gemini chat example using the client API.
This script demonstrates a simple conversation loop with Gemini,
similar to the user's original script but adapted for our app.
"""

import os
from google.generativeai import client
from dotenv import load_dotenv

def run_gemini_chat():
    # Load environment variables
    load_dotenv()
    
    # Load your Gemini API key from environment variable
    API_KEY = os.environ.get("GEMINI_API_KEY")
    
    if not API_KEY:
        print("ERROR: GEMINI_API_KEY not found in environment variables.")
        print("Please set this in your .env file or environment.")
        return
    
    # Configure the client
    client.configure(api_key=API_KEY)
    
    # Initialize empty conversation history
    history = []
    
    # Create the model instance with desired parameters
    model = client.generative_model(
        model="models/gemini-1.5-pro",
        temperature=0.0,          # Controls creativity (0 = deterministic)
        max_output_tokens=1024,   # Max tokens in response
        safety_settings=[{"category": "HARM_CATEGORY_DEROGATORY", "threshold": "BLOCK"}],
        response_format="text"    # Plain text response
    )
    
    print("Bot: Hello! I'm your expense tracking assistant. How can I help you today?")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            print("Bot: Goodbye!")
            break
        
        # Append user message to history
        history.append({"role": "user", "parts": [user_input]})
        
        try:
            # Start a chat session with the current history
            chat_session = model.start_chat(history=history)
            
            # Get the model's response to the latest user input
            response = chat_session.message(user_input)
            
            # Extract the text response
            bot_reply = response.text
            print(f"Bot: {bot_reply}")
            
            # Append bot response to history
            history.append({"role": "model", "parts": [bot_reply]})
            
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Bot: I'm having trouble connecting right now. Please try again later.")

if __name__ == "__main__":
    print("Starting Gemini chat example...")
    run_gemini_chat() 