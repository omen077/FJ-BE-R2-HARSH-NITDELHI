# Gemini AI Integration for Expense Tracker

This module integrates Google's Gemini AI model with the Django expense tracker application to provide a conversational interface for managing expenses.

## Setup Instructions

1. **Get a Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create an API key if you don't have one already
   - Copy your API key

2. **Add API Key to Environment**
   - Add the following line to your `.env` file:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

3. **Install Required Packages**
   ```
   pip install google-generativeai>=0.7.0 python-dotenv
   ```

## Testing the Integration

To test if your Gemini API is working correctly:

1. Run the test script:
   ```
   python chatbot/test_gemini_client.py
   ```

2. Try the standalone chat example:
   ```
   python chatbot/gemini_chat_example.py
   ```

## Understanding the Implementation

### Key Files:
- `gemini_handler.py`: Main class for interfacing with Gemini API
- `views.py`: Django views for the chatbot interface
- `models.py`: Database models for chat messages
- `test_gemini_client.py`: Script to test your API key and connection
- `gemini_chat_example.py`: Standalone example of a chat session

### Key Functions:
- `GeminiChatBot.process_message()`: Processes user messages and returns AI responses
- `process_message()` view: Handles HTTP requests to the chatbot

## Troubleshooting

If you encounter errors:

1. **API Key Issues**
   - Ensure your API key is correctly set in the `.env` file
   - Check that the `.env` file is being loaded properly

2. **Import Errors**
   - Ensure you have installed google-generativeai version 0.7.0 or higher
   - The error `module 'google.generativeai' has no attribute 'GenerativeModel'` occurs with outdated versions

3. **Model Not Available**
   - If the specified model is not available, try changing to "gemini-1.5-flash" in `gemini_handler.py`

## Using the Chatbot

Once set up, the chatbot can help with:
- Adding new expenses
- Viewing expense history
- Getting spending statistics
- Managing expense categories 