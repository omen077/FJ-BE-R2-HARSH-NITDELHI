from django.contrib import admin
from django.contrib.auth.models import User

from .models import *

# Register your models here.


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["pk", "owner", "date", "source", "category", "content", "amount"]


class BudgetAdmin(admin.ModelAdmin):
    list_display = ["pk", "owner", "amount"]


class UserAdmin(admin.ModelAdmin):
    list_display = ["pk", "username", "email", "first_name", "last_name"]


admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Budget, BudgetAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(ReceiptUpload)

admin.site.register(Notification)



admin.site.site_header = "Expense Tracker Admin"
admin.site.site_title = "Expense Tracker Admin Portal"
admin.site.index_title = "Welcome to the Expense Tracker Admin Portal"
admin.site.empty_value_display = "N/A"
