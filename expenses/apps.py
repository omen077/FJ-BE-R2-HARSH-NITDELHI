from django.apps import AppConfig


class ExpensesConfig(AppConfig):
    name = "expenses"
    
    def ready(self):
        import expenses.signals  # This imports the signals module
