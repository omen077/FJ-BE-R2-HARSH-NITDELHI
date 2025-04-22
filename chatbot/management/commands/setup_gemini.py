"""
Django management command to set up Gemini AI API key.
"""

import os
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from dotenv import set_key, load_dotenv

class Command(BaseCommand):
    help = 'Set up Gemini API key for the chatbot'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--key', 
            type=str,
            help='Gemini API key to use (if not provided, the command will prompt for it)'
        )
        
    def handle(self, *args, **options):
        api_key = options.get('key')
        
        # If key is not provided as an argument, prompt for it
        if not api_key:
            if sys.stdin.isatty():  # Check if running in an interactive terminal
                api_key = input('Enter your Gemini API key: ')
            else:
                self.stderr.write(self.style.ERROR(
                    'No API key provided. Use --key option or run in an interactive terminal.'
                ))
                return
        
        if not api_key:
            self.stderr.write(self.style.ERROR('API key cannot be empty.'))
            return
        
        # Determine the path to the .env file
        env_path = os.path.join(settings.BASE_DIR, '.env')
        
        # Ensure the .env file exists
        if not os.path.exists(env_path):
            with open(env_path, 'w') as f:
                f.write('# Environment variables for django-expense-tracker\n')
        
        # Set the API key in the .env file
        try:
            load_dotenv(env_path)
            set_key(env_path, 'GEMINI_API_KEY', api_key)
            self.stdout.write(self.style.SUCCESS('✓ Successfully set Gemini API key in .env file'))
            self.stdout.write(self.style.WARNING(
                'Note: You need to restart the server for the changes to take effect.'
            ))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error setting API key: {str(e)}'))
            
        # Verify the key has been set
        load_dotenv(env_path)
        if os.environ.get('GEMINI_API_KEY') == api_key:
            self.stdout.write(self.style.SUCCESS('✓ Verified API key is correctly set in environment'))
        else:
            self.stderr.write(self.style.ERROR('API key was not correctly set in the environment')) 