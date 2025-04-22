"""
Gemini API handler for the expense tracker chatbot.
This module integrates Google's Gemini model to handle natural language processing
and function calling for expense management.
"""

import os
import json
from django.conf import settings
from dotenv import load_dotenv

# Initialize Gemini client
load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_INITIALIZED = False

try:
    if API_KEY:
        # Initialize with the API key using the client API style
        from google.generativeai import client
        client.configure(api_key=API_KEY)
        GEMINI_INITIALIZED = True
        print("Successfully connected to the Gemini AI model!")
    else:
        print("Warning: GEMINI_API_KEY environment variable not set")
except Exception as e:
    print(f"Error initializing Gemini: {str(e)}")

# Model configuration - using the model specified in your script
MODEL_ID = "models/gemini-1.5-pro"

# System prompt that defines what the chatbot can do
SYSTEM_PROMPT = """
You are an expense tracker assistant that helps users manage their personal finances.
Your main purpose is to help users:
1. Add new expenses
2. View their expense history
3. Edit existing expenses
4. Delete expenses
5. Get statistics about their spending

You should respond naturally to user queries, maintain a friendly tone, and help users accomplish these tasks efficiently.
Always extract the relevant expense details like amount, category, date, and description when applicable.

When the user wants to perform an action, call the appropriate function to handle it.
"""

# Define functions that Gemini can call - Note: May not be supported in all versions
FUNCTION_DECLARATIONS = [
    {
        "name": "add_expense",
        "description": "Add a new expense record",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "number",
                    "description": "The expense amount in currency"
                },
                "category": {
                    "type": "string",
                    "description": "The expense category (e.g., food, transportation, entertainment)"
                },
                "date": {
                    "type": "string",
                    "description": "The date of the expense (YYYY-MM-DD format or relative like 'today', 'yesterday')"
                },
                "description": {
                    "type": "string",
                    "description": "A brief description of the expense (optional)"
                }
            },
            "required": ["amount", "category"]
        }
    },
    {
        "name": "view_expenses",
        "description": "Retrieve expense records based on filters",
        "parameters": {
            "type": "object",
            "properties": {
                "timeframe": {
                    "type": "string",
                    "description": "The time period to retrieve expenses for (e.g., today, this week, this month, custom date range)"
                },
                "category": {
                    "type": "string",
                    "description": "Filter by expense category"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of expenses to return (default: 5)"
                },
                "amount_min": {
                    "type": "number",
                    "description": "Minimum expense amount filter"
                },
                "amount_max": {
                    "type": "number",
                    "description": "Maximum expense amount filter"
                }
            }
        }
    },
    {
        "name": "edit_expense",
        "description": "Edit an existing expense record",
        "parameters": {
            "type": "object",
            "properties": {
                "expense_id": {
                    "type": "integer",
                    "description": "The ID of the expense to edit"
                },
                "field": {
                    "type": "string",
                    "description": "The field to update (amount, category, date, description)",
                    "enum": ["amount", "category", "date", "description"]
                },
                "value": {
                    "type": "string",
                    "description": "The new value for the specified field"
                }
            },
            "required": ["expense_id", "field", "value"]
        }
    },
    {
        "name": "delete_expense",
        "description": "Delete an expense record",
        "parameters": {
            "type": "object",
            "properties": {
                "expense_id": {
                    "type": "integer",
                    "description": "The ID of the expense to delete"
                },
                "confirm": {
                    "type": "boolean",
                    "description": "Confirmation to delete the expense"
                }
            },
            "required": ["expense_id"]
        }
    },
    {
        "name": "get_statistics",
        "description": "Get statistics about expenses",
        "parameters": {
            "type": "object",
            "properties": {
                "timeframe": {
                    "type": "string",
                    "description": "The time period to analyze (e.g., this week, this month, this year)"
                },
                "category": {
                    "type": "string",
                    "description": "Get statistics for a specific category"
                },
                "group_by": {
                    "type": "string",
                    "description": "How to group the statistics (e.g., category, day, week, month)",
                    "enum": ["category", "day", "week", "month"]
                }
            }
        }
    }
]

class GeminiChatBot:
    """
    A chatbot interface using Google's Gemini model.
    """
    
    def __init__(self, api_handler=None):
        """
        Initialize the Gemini chatbot.
        
        Args:
            api_handler: The API handler for expense operations
        """
        if not GEMINI_INITIALIZED:
            raise ValueError("Gemini API is not properly initialized. Please check your API key.")
        
        print(f"Initializing Gemini chatbot with model: {MODEL_ID}")
        
        # Store API handler
        self.api_handler = api_handler
        
        # Create a model instance with the client API style
        from google.generativeai import client
        self.model = client.generative_model(
            model=MODEL_ID,
            temperature=0.0,
            max_output_tokens=1024,
            response_format="text"
        )
        
        # Initialize empty conversation history
        self.history = []
    
    def process_message(self, message, user_context=None):
        """
        Process a user message through Gemini and return a response.
        
        Args:
            message (str): The user's message
            user_context (dict): User-specific context information
            
        Returns:
            dict: A response object with message text and any context/action information
        """
        if user_context is None:
            user_context = {}
        
        try:
            # Add system prompt as a prefix only on the first message
            if not self.history:
                # Append initial system prompt to history
                self.history.append({"role": "model", "parts": [SYSTEM_PROMPT]})
                print("Adding system prompt to conversation history")

            # Add user message to history
            self.history.append({"role": "user", "parts": [message]})
            
            print(f"Generating response for: {message}")
            
            # Start a chat session with the current history
            chat_session = self.model.start_chat(history=self.history)
            
            try:
                # Get the model's response to the latest user input
                response = chat_session.message(message)
                
                # Extract the text response
                response_text = response.text
                print(f"Response received: {response_text[:50]}...")
                
                # Add the response to history
                self.history.append({"role": "model", "parts": [response_text]})
                
                # Return the response in the expected format
                return {
                    'message': response_text,
                    'success': True,
                    'context': user_context
                }
                
            except Exception as chat_error:
                print(f"Error in chat session: {str(chat_error)}")
                return {
                    'message': f"I'm having trouble generating a response: {str(chat_error)}",
                    'success': False,
                    'context': user_context
                }
                
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            return {
                'message': f"An error occurred: {str(e)}",
                'success': False,
                'context': user_context
            }
    
    def _handle_function_call(self, function_name, args, user_context):
        """
        Handle function calls by routing to the API handler.
        
        Args:
            function_name (str): The name of the function to call
            args (dict): The arguments for the function
            user_context (dict): User context information
            
        Returns:
            str: JSON string with the function response
        """
        try:
            # Route to the appropriate API handler method
            if function_name == "add_expense":
                result = self.api_handler._handle_add_expense(args)
            elif function_name == "view_expenses":
                result = self.api_handler._handle_view_expenses(args)
            elif function_name == "edit_expense":
                result = self.api_handler._handle_edit_expense(args)
            elif function_name == "delete_expense":
                result = self.api_handler._handle_delete_expense(args)
            elif function_name == "get_statistics":
                result = self.api_handler._handle_get_statistics(args)
            else:
                return json.dumps({
                    "error": f"Unknown function: {function_name}"
                })
            
            return json.dumps(result)
        
        except Exception as e:
            return json.dumps({
                "error": str(e)
            })
    
    def _mock_function_response(self, function_name, args):
        """
        Provide mock responses for testing without an API handler.
        
        Args:
            function_name (str): The name of the function to mock
            args (dict): The arguments for the function
            
        Returns:
            str: JSON string with a mock response
        """
        if function_name == "add_expense":
            return json.dumps({
                "success": True,
                "message": f"Successfully added expense of ${args.get('amount')} for {args.get('category')}.",
                "expense_id": 123
            })
        
        elif function_name == "view_expenses":
            return json.dumps({
                "success": True,
                "expenses": [
                    {"id": 1, "amount": 45.00, "category": "Groceries", "date": "2023-04-20", "description": "Weekly shopping"},
                    {"id": 2, "amount": 12.99, "category": "Entertainment", "date": "2023-04-19", "description": "Movie tickets"},
                    {"id": 3, "amount": 35.50, "category": "Dining", "date": "2023-04-18", "description": "Dinner with friends"}
                ]
            })
        
        elif function_name == "edit_expense":
            return json.dumps({
                "success": True,
                "message": f"Successfully updated expense {args.get('expense_id')}.",
                "updated_field": args.get('field'),
                "updated_value": args.get('value')
            })
        
        elif function_name == "delete_expense":
            if args.get('confirm'):
                return json.dumps({
                    "success": True,
                    "message": f"Successfully deleted expense {args.get('expense_id')}."
                })
            else:
                return json.dumps({
                    "success": False,
                    "message": "Please confirm deletion by setting confirm to true.",
                    "requires_confirmation": True
                })
        
        elif function_name == "get_statistics":
            return json.dumps({
                "success": True,
                "timeframe": args.get('timeframe', 'this month'),
                "total": 523.45,
                "top_categories": [
                    {"category": "Groceries", "amount": 210.30},
                    {"category": "Dining", "amount": 125.75},
                    {"category": "Entertainment", "amount": 95.50}
                ]
            })
        
        else:
            return json.dumps({
                "error": f"Unknown function: {function_name}"
            }) 