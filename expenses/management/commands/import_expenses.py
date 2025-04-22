import json
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from expenses.models import Expense

class Command(BaseCommand):
    help = 'Imports expense data from expenses/data.json file'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to assign expenses to')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist'))
            return
        
        try:
            with open('expenses/data.json') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('File expenses/data.json not found'))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('Invalid JSON format in expenses/data.json'))
            return
        
        # Map the time periods to dates
        date_mapping = {
            'today': datetime.now().strftime('%Y-%m-%d'),
            'one_week_ago': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'two_weeks_ago': (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d'),
            'three_weeks_ago': (datetime.now() - timedelta(days=21)).strftime('%Y-%m-%d'),
            'one_month_ago': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'two_month_ago': (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'),
            'three_month_ago': (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        }
        
        expenses_to_create = []
        
        # Process each time period in the data
        for time_period, expenses_list in data.items():
            for expense_data in expenses_list:
                expenses_to_create.append({
                    'amount': expense_data['amount'],
                    'content': expense_data['content'],
                    'category': expense_data['category'],
                    'source': expense_data['source'],
                    'date': date_mapping[time_period],
                    'owner': user
                })
        
        # Create the expenses
        counter = 0
        for expense_data in expenses_to_create:
            expense = Expense(
                amount=expense_data['amount'],
                content=expense_data['content'],
                category=expense_data['category'],
                source=expense_data['source'],
                date=expense_data['date'],
                owner=expense_data['owner']
            )
            expense.save()
            counter += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {counter} expenses for user {username}')
        ) 