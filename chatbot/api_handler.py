"""
API Handler for the chatbot.

This module handles API operations for expense management,
designed to be used with the Gemini function calling framework.
"""

import json
import requests
from django.urls import reverse
from dateutil import parser
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta

class ExpenseAPIHandler:
    """
    Handles API calls for expense operations.
    """
    
    def __init__(self, request):
        """
        Initialize the API handler with the request context.
        
        Args:
            request: The Django request object
        """
        self.request = request
        self.user = request.user
        self.host = request.get_host()
        self.scheme = request.scheme
    
    def _handle_add_expense(self, args):
        """
        Handle adding a new expense.
        
        Args:
            args (dict): Arguments from Gemini function call
            
        Returns:
            dict: API response
        """
        # Extract fields
        amount = args.get('amount')
        category = args.get('category')
        date_str = args.get('date', 'today')
        description = args.get('description', '')
        
        # Validate required fields
        if not amount:
            return {
                'success': False,
                'message': "Amount is required to add an expense."
            }
            
        if not category:
            return {
                'success': False,
                'message': "Category is required to add an expense."
            }
        
        # Process date
        try:
            parsed_date = self._parse_date(date_str)
        except ValueError:
            return {
                'success': False,
                'message': f"Could not parse date: {date_str}. Please use YYYY-MM-DD format or a relative date like 'today' or 'yesterday'."
            }
        
        # For production, this would call the actual API
        # For now, we'll just return a mock response
        
        return {
            'success': True,
            'message': f"Successfully added expense of ${amount:.2f} for {category} on {parsed_date.strftime('%Y-%m-%d')}.",
            'expense_id': 123,  # Mock ID
            'data': {
                'amount': amount,
                'category': category,
                'date': parsed_date.strftime('%Y-%m-%d'),
                'description': description
            }
        }
    
    def _handle_view_expenses(self, args):
        """
        Handle viewing expenses.
        
        Args:
            args (dict): Arguments from Gemini function call
            
        Returns:
            dict: API response with expense data
        """
        # Extract filter criteria
        timeframe = args.get('timeframe', 'recent')
        category = args.get('category')
        limit = args.get('limit', 5)
        amount_min = args.get('amount_min')
        amount_max = args.get('amount_max')
        
        # For production, this would call the actual API
        # For now, we'll just return mock data
        
        # Mock expenses data
        expenses = [
            {"id": 1, "amount": 45.00, "category": "Groceries", "date": "2023-04-20", "description": "Weekly shopping"},
            {"id": 2, "amount": 12.99, "category": "Entertainment", "date": "2023-04-19", "description": "Movie tickets"},
            {"id": 3, "amount": 35.50, "category": "Dining", "date": "2023-04-18", "description": "Dinner with friends"},
            {"id": 4, "amount": 22.75, "category": "Transportation", "date": "2023-04-17", "description": "Uber ride"},
            {"id": 5, "amount": 5.99, "category": "Entertainment", "date": "2023-04-16", "description": "App purchase"}
        ]
        
        # Apply filters (for a real implementation)
        if category:
            expenses = [e for e in expenses if e["category"].lower() == category.lower()]
        
        if amount_min is not None:
            expenses = [e for e in expenses if e["amount"] >= amount_min]
            
        if amount_max is not None:
            expenses = [e for e in expenses if e["amount"] <= amount_max]
        
        # Apply limit
        expenses = expenses[:limit]
        
        # Create formatted expense strings for display
        formatted_expenses = []
        for i, expense in enumerate(expenses, 1):
            formatted_expense = (
                f"{i}. ${expense['amount']:.2f} - {expense['category']} "
                f"({expense['date']}){'- ' + expense['description'] if expense['description'] else ''}"
            )
            formatted_expenses.append(formatted_expense)
        
        # Build response message
        if not expenses:
            message = "No expenses found matching your criteria."
        else:
            filter_desc = []
            if timeframe and timeframe.lower() != 'recent':
                filter_desc.append(f"from {timeframe}")
            if category:
                filter_desc.append(f"in category '{category}'")
            if amount_min is not None or amount_max is not None:
                amount_filter = ""
                if amount_min is not None:
                    amount_filter += f"at least ${amount_min:.2f}"
                if amount_max is not None:
                    if amount_filter:
                        amount_filter += " and "
                    amount_filter += f"at most ${amount_max:.2f}"
                filter_desc.append(f"with {amount_filter}")
            
            filter_text = " ".join(filter_desc) if filter_desc else ""
            
            if filter_text:
                message = f"Here are your expenses {filter_text}:\n\n" + "\n".join(formatted_expenses)
            else:
                message = f"Here are your recent expenses:\n\n" + "\n".join(formatted_expenses)
        
        return {
            'success': True,
            'message': message,
            'expenses': expenses
        }
    
    def _handle_edit_expense(self, args):
        """
        Handle editing an expense.
        
        Args:
            args (dict): Arguments from Gemini function call
            
        Returns:
            dict: API response
        """
        # Extract fields
        expense_id = args.get('expense_id')
        field = args.get('field')
        value = args.get('value')
        
        # Validate required fields
        if not expense_id:
            return {
                'success': False,
                'message': "Please specify which expense you want to edit by providing an expense ID."
            }
            
        if not field:
            return {
                'success': False,
                'message': "Please specify which field you want to update (amount, category, date, or description)."
            }
            
        if not value:
            return {
                'success': False,
                'message': f"Please provide a new value for the {field}."
            }
        
        # Process value based on field type
        if field == 'amount':
            try:
                value = float(value)
            except ValueError:
                return {
                    'success': False,
                    'message': f"Invalid amount: {value}. Please provide a valid number."
                }
        elif field == 'date':
            try:
                parsed_date = self._parse_date(value)
                value = parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                return {
                    'success': False,
                    'message': f"Could not parse date: {value}. Please use YYYY-MM-DD format or a relative date like 'today' or 'yesterday'."
                }
        
        # For production, this would call the actual API
        # For now, we'll just return a mock response
        
        return {
            'success': True,
            'message': f"Successfully updated the {field} of expense #{expense_id} to {value}.",
            'data': {
                'expense_id': expense_id,
                'field': field,
                'value': value
            }
        }
    
    def _handle_delete_expense(self, args):
        """
        Handle deleting an expense.
        
        Args:
            args (dict): Arguments from Gemini function call
            
        Returns:
            dict: API response
        """
        # Extract fields
        expense_id = args.get('expense_id')
        confirm = args.get('confirm', False)
        
        # Validate required fields
        if not expense_id:
            return {
                'success': False,
                'message': "Please specify which expense you want to delete by providing an expense ID."
            }
        
        # Require confirmation
        if not confirm:
            return {
                'success': False,
                'message': f"Are you sure you want to delete expense #{expense_id}? This cannot be undone. Please confirm.",
                'requires_confirmation': True,
                'data': {
                    'expense_id': expense_id
                }
            }
        
        # For production, this would call the actual API
        # For now, we'll just return a mock response
        
        return {
            'success': True,
            'message': f"Successfully deleted expense #{expense_id}.",
            'data': {
                'expense_id': expense_id
            }
        }
    
    def _handle_get_statistics(self, args):
        """
        Handle getting statistics about expenses.
        
        Args:
            args (dict): Arguments from Gemini function call
            
        Returns:
            dict: API response with statistics
        """
        # Extract fields
        timeframe = args.get('timeframe', 'this month')
        category = args.get('category')
        group_by = args.get('group_by', 'category')
        
        # For production, this would call the actual API
        # For now, we'll just return mock data
        
        # Mock statistics
        statistics = {
            'total': 523.45,
            'top_categories': [
                {"category": "Groceries", "amount": 210.30},
                {"category": "Dining", "amount": 125.75},
                {"category": "Entertainment", "amount": 95.50},
                {"category": "Transportation", "amount": 65.90},
                {"category": "Utilities", "amount": 26.00}
            ],
            'timeframe': timeframe
        }
        
        # Format statistics into a readable message
        message = f"Here's a summary of your spending for {timeframe}:\n\n"
        message += f"Total: ${statistics['total']:.2f}\n\n"
        message += "Top categories:\n"
        
        for i, cat in enumerate(statistics['top_categories'], 1):
            message += f"{i}. {cat['category']}: ${cat['amount']:.2f}\n"
        
        return {
            'success': True,
            'message': message,
            'statistics': statistics
        }
    
    def _parse_date(self, date_str):
        """
        Parse a date string into a datetime object.
        Handles relative dates like 'today', 'yesterday', as well as standard formats.
        
        Args:
            date_str (str): The date string to parse
            
        Returns:
            datetime: The parsed date
            
        Raises:
            ValueError: If the date string cannot be parsed
        """
        date_str = date_str.lower().strip()
        
        today = date.today()
        
        if date_str == 'today':
            return today
        elif date_str == 'yesterday':
            return today - timedelta(days=1)
        elif date_str == 'tomorrow':
            return today + timedelta(days=1)
        elif date_str.startswith('last '):
            unit = date_str[5:]
            if unit == 'week':
                return today - timedelta(days=7)
            elif unit == 'month':
                return today - relativedelta(months=1)
            elif unit == 'year':
                return today - relativedelta(years=1)
            else:
                # Try to parse as "last Monday", "last Tuesday", etc.
                days = {
                    'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                    'friday': 4, 'saturday': 5, 'sunday': 6
                }
                if unit in days:
                    target_day = days[unit]
                    current_day = today.weekday()
                    delta = (current_day - target_day) % 7
                    if delta == 0:
                        delta = 7  # If today is the target day, go back a week
                    return today - timedelta(days=delta)
        elif date_str.startswith('this '):
            unit = date_str[5:]
            if unit == 'week':
                # Return the start of the current week (Monday)
                current_day = today.weekday()
                return today - timedelta(days=current_day)
            elif unit == 'month':
                # Return the start of the current month
                return date(today.year, today.month, 1)
            elif unit == 'year':
                # Return the start of the current year
                return date(today.year, 1, 1)
        
        # Try to parse as a regular date
        try:
            return parser.parse(date_str).date()
        except (ValueError, parser.ParserError):
            raise ValueError(f"Could not parse date: {date_str}") 