"""
Test script for Gemini integration using the client API.
Run this script directly to test your Gemini API key and connection.
"""

import os
from google.generativeai import client
from dotenv import load_dotenv

def test_gemini_client():
    # Load environment variables
    load_dotenv()
    
    # Load your Gemini API key from environment variable
    API_KEY = os.environ.get("GEMINI_API_KEY")
    
    if not API_KEY:
        print("ERROR: GEMINI_API_KEY not found in environment variables.")
        print("Please set this in your .env file or environment.")
        return False
    
    try:
        # Configure the client
        client.configure(api_key=API_KEY)
        print("Successfully configured Gemini client.")
        
        # Create the model instance with desired parameters
        model = client.generative_model(
            model="models/gemini-1.5-pro",
            temperature=0.0,          # Controls creativity (0 = deterministic)
            max_output_tokens=1024,   # Max tokens in response
            response_format="text"    # Plain text response
        )
        
        print("Successfully created model instance.")
        print(f"Testing with a simple query...")
        
        # Test with a simple message
        response = model.generate_content("Hello, what can you help me with regarding expense tracking?")
        
        if hasattr(response, 'text'):
            print("Success! Got response from Gemini:")
            print(f"Response: {response.text[:200]}...")
            return True
        else:
            print("Error: Response doesn't have expected 'text' attribute.")
            print(f"Response object: {response}")
            return False
            
    except Exception as e:
        print(f"Error testing Gemini client: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Gemini client API integration...")
    result = test_gemini_client()
    if result:
        print("✅ Gemini client API test passed!")
    else:
        print("❌ Gemini client API test failed!") 