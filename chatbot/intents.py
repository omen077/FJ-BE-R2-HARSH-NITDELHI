"""
Intent recognition for the chatbot.
This module defines the different intents that can be recognized from user messages
and the corresponding actions to take.
"""

# Define intent categories
INTENT_ADD_EXPENSE = 'add_expense'
INTENT_VIEW_EXPENSES = 'view_expenses'
INTENT_EDIT_EXPENSE = 'edit_expense'
INTENT_DELETE_EXPENSE = 'delete_expense'
INTENT_GET_STATISTICS = 'get_statistics'
INTENT_UNKNOWN = 'unknown'
INTENT_GREETING = 'greeting'
INTENT_HELP = 'help'
INTENT_THANKS = 'thanks'

# Intent patterns - keywords and phrases that might indicate each intent
INTENT_PATTERNS = {
    INTENT_ADD_EXPENSE: [
        'add expense', 'create expense', 'new expense', 'record expense', 
        'spent', 'bought', 'purchased', 'paid', 'pay for', 
        'add a new', 'log expense', 'track expense'
    ],
    
    INTENT_VIEW_EXPENSES: [
        'show expenses', 'view expenses', 'list expenses', 'get expenses', 
        'see expenses', 'display expenses', 'what did i spend', 'my expenses',
        'recent expenses', 'spending history', 'transaction history'
    ],
    
    INTENT_EDIT_EXPENSE: [
        'edit expense', 'update expense', 'change expense', 'modify expense',
        'fix expense', 'correct expense', 'update the', 'change the'
    ],
    
    INTENT_DELETE_EXPENSE: [
        'delete expense', 'remove expense', 'erase expense', 'get rid of expense',
        'drop expense', 'cancel expense'
    ],
    
    INTENT_GET_STATISTICS: [
        'statistics', 'stats', 'summary', 'overview', 'report', 'analysis',
        'how much did i spend', 'total spending', 'spending by', 'charts'
    ],
    
    INTENT_GREETING: [
        'hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon',
        'good evening', 'what\'s up', 'howdy'
    ],
    
    INTENT_HELP: [
        'help', 'assist', 'support', 'guide', 'what can you do', 'how to',
        'instructions', 'show me how', 'commands', 'features'
    ],
    
    INTENT_THANKS: [
        'thanks', 'thank you', 'appreciate it', 'grateful', 'thank', 'thx'
    ]
}

# Responses for simple intents that don't require API calls
STATIC_RESPONSES = {
    INTENT_GREETING: [
        "Hello! How can I help you with your expenses today?",
        "Hi there! Need help with your expense tracking?",
        "Hey! I'm your expense assistant. What would you like to do?",
        "Greetings! Ready to manage your expenses?"
    ],
    
    INTENT_HELP: [
        "I can help you manage expenses. Try saying things like:\n"
        "- 'Add an expense of $45 for dinner yesterday'\n"
        "- 'Show my expenses from last week'\n"
        "- 'What did I spend on groceries this month?'\n"
        "- 'Edit my last expense'\n"
        "- 'Delete the $20 transportation expense'"
    ],
    
    INTENT_THANKS: [
        "You're welcome! Anything else you need help with?",
        "Happy to help! Need anything else?",
        "My pleasure. What else can I assist you with today?",
        "Anytime! Let me know if you need more help."
    ],
    
    INTENT_UNKNOWN: [
        "I'm not sure I understand. Could you rephrase that?",
        "I didn't quite get that. Can you be more specific about what you need?",
        "Sorry, I don't understand. Try asking in a different way or type 'help' to see what I can do."
    ]
}

# Information extraction patterns for each intent
# These will be used to extract relevant information from the message
EXTRACTION_PATTERNS = {
    INTENT_ADD_EXPENSE: {
        'amount': [
            r'\$\s?(\d+\.?\d*)',  # $50 or $50.25
            r'(\d+\.?\d*)\s?dollars',  # 50 dollars or 50.25 dollars
            r'(\d+\.?\d*)\s?inr',  # 50 inr or 50.25 inr
            r'rs\.?\s?(\d+\.?\d*)',  # Rs 50 or Rs 50.25
            r'(\d+\.?\d*)\s?rupees',  # 50 rupees or 50.25 rupees
            r'spend\s?(\d+\.?\d*)',  # spend 50 or spend 50.25
            r'spent\s?(\d+\.?\d*)',  # spent 50 or spent 50.25
            r'cost\s?(\d+\.?\d*)',  # cost 50 or cost 50.25
            r'(\d+\.?\d*)\s?for',  # 50 for or 50.25 for
        ],
        'category': [
            r'for\s([a-z\s]+)',  # for groceries
            r'on\s([a-z\s]+)',  # on food
            r'category\s([a-z\s]+)',  # category utilities
            r'in\s([a-z\s]+)\scategory',  # in entertainment category
        ],
        'date': [
            r'on\s(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',  # on 01/25/2023
            r'yesterday',
            r'today',
            r'tomorrow',
            r'last\s(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'next\s(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'last\s(week|month)',
            r'this\s(week|month)',
        ],
        'description': [
            r'description\s["\'](.+)["\']',  # description "lunch with friends"
            r'note\s["\'](.+)["\']',  # note "team lunch"
            r'memo\s["\'](.+)["\']',  # memo "business expense"
        ]
    },
    
    INTENT_VIEW_EXPENSES: {
        'timeframe': [
            r'today',
            r'yesterday',
            r'this\s(week|month|year)',
            r'last\s(week|month|year)',
            r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',  # 01/25/2023
            r'from\s(.+)\sto\s(.+)',  # from January to March
        ],
        'category': [
            r'in\s([a-z\s]+)',  # in groceries
            r'for\s([a-z\s]+)',  # for food
            r'category\s([a-z\s]+)',  # category utilities
            r'([a-z\s]+)\scategory',  # entertainment category
        ],
        'amount': [
            r'above\s\$?(\d+\.?\d*)',  # above $50
            r'below\s\$?(\d+\.?\d*)',  # below $50
            r'more than\s\$?(\d+\.?\d*)',  # more than $50
            r'less than\s\$?(\d+\.?\d*)',  # less than $50
        ],
        'limit': [
            r'last\s(\d+)',  # last 5
            r'recent\s(\d+)',  # recent 10
            r'top\s(\d+)',  # top 3
        ]
    },
    
    INTENT_EDIT_EXPENSE: {
        'identifier': [
            r'expense\s?#?(\d+)',  # expense #12
            r'id\s?#?(\d+)',  # id #15
            r'transaction\s?#?(\d+)',  # transaction #20
            r'last\sexpense',  # last expense
        ],
        'field': [
            r'change\s(amount|category|date|description)',  # change amount
            r'update\s(amount|category|date|description)',  # update category
            r'edit\s(amount|category|date|description)',  # edit date
            r'modify\s(amount|category|date|description)',  # modify description
        ],
        'new_value': [
            r'to\s\$?(\d+\.?\d*)',  # to $50 or to 50
            r'to\s([a-z\s]+)\scategory',  # to groceries category
            r'to\s(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',  # to 01/25/2023
            r'to\s["\'](.+)["\']',  # to "lunch with team"
        ]
    },
    
    INTENT_DELETE_EXPENSE: {
        'identifier': [
            r'expense\s?#?(\d+)',  # expense #12
            r'id\s?#?(\d+)',  # id #15
            r'transaction\s?#?(\d+)',  # transaction #20
            r'last\sexpense',  # last expense
        ],
        'confirmation': [
            r'yes',
            r'confirm',
            r'proceed',
            r'go ahead',
            r'delete it',
            r'remove it',
        ]
    }
}

def detect_intent(message):
    """
    Analyze the user message and determine the most likely intent
    
    Args:
        message (str): The user's message
        
    Returns:
        str: The detected intent
    """
    # Convert message to lowercase for case-insensitive matching
    message_lower = message.lower()
    
    # Check for each intent by looking for patterns
    highest_match_count = 0
    detected_intent = INTENT_UNKNOWN
    
    for intent, patterns in INTENT_PATTERNS.items():
        match_count = 0
        for pattern in patterns:
            if pattern in message_lower:
                match_count += 1
        
        # If this intent has more matches than previous best, update detected intent
        if match_count > highest_match_count:
            highest_match_count = match_count
            detected_intent = intent
    
    return detected_intent


def extract_info(message, intent):
    """
    Extract relevant information from the message based on the detected intent
    
    Args:
        message (str): The user's message
        intent (str): The detected intent
        
    Returns:
        dict: Dictionary of extracted information
    """
    import re
    
    # Convert message to lowercase for case-insensitive matching
    message_lower = message.lower()
    
    # Initialize extracted info with the intent
    extracted_info = {
        'intent': intent,
        'raw_message': message
    }
    
    # If we don't have extraction patterns for this intent or it's a simple intent, return
    if intent not in EXTRACTION_PATTERNS:
        return extracted_info
    
    # Get the extraction patterns for this intent
    patterns = EXTRACTION_PATTERNS[intent]
    
    # Apply regex patterns for each field we want to extract
    for field, field_patterns in patterns.items():
        for pattern in field_patterns:
            # Special handling for simple patterns that are just strings
            if not pattern.startswith('r') and not '(' in pattern:
                if pattern in message_lower:
                    extracted_info[field] = pattern
                    break
            else:
                # Use regex for complex patterns
                match = re.search(pattern, message_lower)
                if match:
                    # If there's a capture group, use that
                    if match.groups():
                        extracted_info[field] = match.group(1)
                    # Otherwise use the whole match
                    else:
                        extracted_info[field] = match.group(0)
                    break
    
    # Special post-processing for certain fields
    
    # Convert amount to float if present
    if 'amount' in extracted_info:
        try:
            extracted_info['amount'] = float(extracted_info['amount'])
        except ValueError:
            # If we can't convert to float, remove it
            del extracted_info['amount']
    
    # Clean up category if present (remove trailing 'for', 'on', etc.)
    if 'category' in extracted_info:
        category = extracted_info['category'].strip()
        # Remove common prepositions at the end
        for prep in ['for', 'on', 'in', 'at', 'by']:
            if category.endswith(f" {prep}"):
                category = category[:-len(f" {prep}")]
        extracted_info['category'] = category.strip()
    
    # Process date if present
    if 'date' in extracted_info:
        # Handle relative dates like "yesterday", "today", etc.
        # In a real implementation, this would convert to an actual date
        pass
    
    return extracted_info


def get_static_response(intent):
    """
    Get a static response for intents that don't require API calls
    
    Args:
        intent (str): The detected intent
        
    Returns:
        str: A appropriate response message
    """
    # Handle intents with static responses
    if intent in STATIC_RESPONSES:
        import random
        responses = STATIC_RESPONSES[intent]
        return random.choice(responses)
    
    return None 