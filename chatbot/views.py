from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import os
import random

from .models import ChatMessage
from .api_handler import ExpenseAPIHandler
from .gemini_handler import GeminiChatBot
from .intents import detect_intent, extract_info, get_static_response, INTENT_ADD_EXPENSE, INTENT_VIEW_EXPENSES, INTENT_EDIT_EXPENSE, INTENT_DELETE_EXPENSE, INTENT_GET_STATISTICS, INTENT_UNKNOWN

# Check if Gemini API key is set and initialize the chatbot
GEMINI_ENABLED = False  # Disabled for now while preserving the code

@login_required
def chat_history(request):
    """Returns the chat history for the current user"""
    messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
    return render(request, 'chatbot/chat.html', {
        'messages': messages,
        'GEMINI_ENABLED': GEMINI_ENABLED
    })

@login_required
def documentation(request):
    """Returns the documentation page for the chatbot"""
    return render(request, 'chatbot/documentation.html', {
        'GEMINI_ENABLED': GEMINI_ENABLED
    })

@login_required
@require_POST
@csrf_exempt
def process_message(request):
    """Process a message from the user and return a response"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Save user message
        ChatMessage.objects.create(
            user=request.user,
            content=user_message,
            message_type='user'
        )
        
        # Get conversation context (if any)
        context = data.get('context', {})
        
        # Initialize API handler
        api_handler = ExpenseAPIHandler(request)
        
        # Process the message with Gemini
        if GEMINI_ENABLED:
            try:
                # Use the Gemini chatbot
                chatbot = GeminiChatBot(api_handler=api_handler)
                response = chatbot.process_message(user_message, context)
                
                bot_response = response.get('message', 'Sorry, something went wrong.')
                success = response.get('success', False)
                requires_confirmation = response.get('requires_confirmation', False)
                context = response.get('context', {})
            except ValueError as e:
                # Configuration errors
                print(f"Gemini Configuration Error: {str(e)}")
                bot_response = f"The Gemini API is not properly configured: {str(e)}"
                success = False
                requires_confirmation = False
                context = {}
            except AttributeError as e:
                # Likely API version compatibility issues
                print(f"Gemini API Compatibility Error: {str(e)}")
                bot_response = "There's a compatibility issue with the Gemini API. The administrator should update the code or the API version."
                success = False
                requires_confirmation = False
                context = {}
            except Exception as e:
                import traceback
                print(f"Gemini Error: {str(e)}")
                print(traceback.format_exc())
                # Fallback to a simple response if Gemini errors out
                bot_response = f"Sorry, there was an error processing your request: {str(e)}"
                success = False
                requires_confirmation = False
                context = {}
        else:
            # Use pattern-based intent detection
            intent = detect_intent(user_message)
            extracted_info = extract_info(user_message, intent)
            
            # Get static response for simple intents
            static_response = get_static_response(intent)
            if static_response:
                bot_response = static_response
                success = True
                requires_confirmation = False
            else:
                # Handle API-based intents
                if intent == INTENT_ADD_EXPENSE:
                    # Extract arguments and call API
                    args = {
                        'amount': extracted_info.get('amount'),
                        'category': extracted_info.get('category'),
                        'date': extracted_info.get('date', 'today'),
                        'description': extracted_info.get('description', '')
                    }
                    result = api_handler._handle_add_expense(args)
                    bot_response = result.get('message', 'Failed to add expense.')
                    success = result.get('success', False)
                    
                elif intent == INTENT_VIEW_EXPENSES:
                    # Extract arguments and call API
                    args = {
                        'timeframe': extracted_info.get('timeframe', 'recent'),
                        'category': extracted_info.get('category'),
                        'limit': extracted_info.get('limit', 5),
                        'amount_min': extracted_info.get('amount_min'),
                        'amount_max': extracted_info.get('amount_max')
                    }
                    result = api_handler._handle_view_expenses(args)
                    bot_response = result.get('message', 'Failed to retrieve expenses.')
                    success = result.get('success', False)
                    
                elif intent == INTENT_EDIT_EXPENSE:
                    # Extract arguments and call API
                    args = {
                        'expense_id': extracted_info.get('identifier'),
                        'field': extracted_info.get('field'),
                        'value': extracted_info.get('new_value')
                    }
                    result = api_handler._handle_edit_expense(args)
                    bot_response = result.get('message', 'Failed to edit expense.')
                    success = result.get('success', False)
                    
                elif intent == INTENT_DELETE_EXPENSE:
                    # Extract arguments and call API
                    args = {
                        'expense_id': extracted_info.get('identifier'),
                        'confirmation': extracted_info.get('confirmation', False)
                    }
                    result = api_handler._handle_delete_expense(args)
                    bot_response = result.get('message', 'Failed to delete expense.')
                    success = result.get('success', False)
                    requires_confirmation = result.get('requires_confirmation', False)
                    
                elif intent == INTENT_GET_STATISTICS:
                    # Extract arguments and call API
                    args = {
                        'timeframe': extracted_info.get('timeframe', 'month'),
                        'category': extracted_info.get('category')
                    }
                    result = api_handler._handle_get_statistics(args)
                    bot_response = result.get('message', 'Failed to retrieve statistics.')
                    success = result.get('success', False)
                    
                else:
                    bot_response = "I'm not sure what you want to do. Try asking for help to see what I can do."
                    success = False
        
        # Save bot response
        system_message = ChatMessage.objects.create(
            user=request.user,
            content=bot_response,
            message_type='system'
        )
        
        # Create response data
        response_data = {
            'message': bot_response,
            'success': success,
            'timestamp': system_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # If we need to maintain context for the next message, include it
        if context:
            response_data['context'] = context
        
        # Add confirmation flag if needed
        if requires_confirmation:
            response_data['requires_confirmation'] = True
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        import traceback
        print(f"View Error: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)
