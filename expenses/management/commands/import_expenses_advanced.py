import json
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from expenses.models import Expense
from expenses.utils import ExpenseGenerator

class Command(BaseCommand):
    help = 'Imports expense data from expenses/data.json file using the ExpenseGenerator class'

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
                expenses_by_date = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('File expenses/data.json not found'))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('Invalid JSON format in expenses/data.json'))
            return
        
        # Use the ExpenseGenerator to generate expenses with proper dates
        expense_generator = ExpenseGenerator(expenses_by_date)
        expenses_data = expense_generator.generate_expenses()
        
        # Create the expenses
        counter = 0
        for expense_data in expenses_data:
            expense = Expense(
                amount=expense_data['amount'],
                content=expense_data['content'],
                category=expense_data['category'],
                source=expense_data['source'],
                date=expense_data['date'],
                owner=user
            )
            expense.save()
            counter += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {counter} expenses for user {username}')
        ) 