from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from expenses import utils


class ExpenseManager(models.Manager):
    def add_testuser_expenses(self, request):
        if str(request.user) == "testuser1":
            test_user_expenses = Expense.objects.filter(owner=request.user)
            if not test_user_expenses:
                Expense.objects.create_test_expenses(request.user)

    def create_test_expenses(self, owner, expenses=None):
        if not expenses:
            expenses_by_date = utils.get_data_from_json("expenses/data/expensesByDate.json")
            eg = utils.ExpenseGenerator(expenses_by_date)
            expenses = eg.generate_expenses()

        for expense in expenses:
            exp = self.model(
                amount=expense["amount"],
                content=expense["content"],
                category=expense["category"],
                source=expense["source"],
                date=expense["date"],
                owner=owner,
            )
            exp.save()

    def delete_testuser_expenses(self, request):
        if str(request.user) in ["testuser1", "testuser3"]:
            Expense.objects.filter(owner=request.user).delete()

    def delete_testuser_budget(self, request):
        if str(request.user) in ["testuser1", "testuser3"]:
            Budget.objects.all().delete()

    def get_user_expenses(self, owner):
        return Expense.objects.filter(owner=owner)

    def get_total_expenses(self, owner):
        total = self.get_user_expenses(owner).aggregate(amount=Sum("amount"))["amount"]
        return utils.safely_round(total)

    def get_max_expense(self, owner):
        return self.get_user_expenses(owner).order_by("amount").last()

    def get_max_expense_content(self, owner):
        max_expense = self.get_max_expense(owner)
        return max_expense.content if max_expense else "There are no expenses yet."

    def get_min_expense(self, owner):
        return self.get_user_expenses(owner).order_by("amount").first()

    def get_min_expense_content(self, owner):
        min_expense = self.get_min_expense(owner)
        return min_expense.content if min_expense else "There are no expenses yet."

    def get_weekly_expense_sum(self, owner, week_timedelta_num=0):
        current_week_num = utils.get_week_iso_num(week_timedelta_num)
        weekly_total = self.get_user_expenses(owner).filter(date__week=current_week_num).aggregate(amount=Sum("amount"))["amount"]
        return utils.safely_round(weekly_total)

    def get_monthly_expense_sum(self, owner, month_timedelta_num=0):
        month_num = utils.get_month_num(month_timedelta_num)
        month_num = 12 if month_num < 1 else month_num
        total = self.get_user_expenses(owner).filter(date__month=month_num).aggregate(amount=Sum("amount"))["amount"]
        return utils.safely_round(total)

    def get_monthly_expense_average(self, owner):
        months = utils.get_months_list()
        monthly_expenses_data = []

        for i, _ in enumerate(months):
            month_num = i + 1
            monthly_expenses = self.get_user_expenses(owner).filter(date__month=month_num)
            if monthly_expenses:
                monthly_sum = monthly_expenses.aggregate(amount=Sum("amount"))["amount"]
                monthly_expenses_data.append(round(monthly_sum, 2))

        return round(sum(monthly_expenses_data) / len(monthly_expenses_data), 2) if monthly_expenses_data else 0

    def get_expense_amounts_by_category(self, owner):
        data = {}
        for exp in self.get_user_expenses(owner):
            data[exp.category] = data.get(exp.category, 0) + float(exp.amount)
        return data

    def get_biggest_category_expenditure(self, owner):
        category_data = self.get_expense_amounts_by_category(owner)
        if not category_data:
            return {"category": "No expenses", "amount": 0}
        max_category = max(category_data, key=category_data.get)
        return {"category": max_category, "amount": round(category_data[max_category], 2)}

    def get_smallest_category_expenditure(self, owner):
        category_data = self.get_expense_amounts_by_category(owner)
        if not category_data:
            return {"category": "No expenses", "amount": 0}
        min_category = min(category_data, key=category_data.get)
        return {"category": min_category, "amount": round(category_data[min_category], 2)}

    def get_curr_and_last_month_expenses_percentage_diff(self, owner):
        curr = self.get_monthly_expense_sum(owner)
        prev = self.get_monthly_expense_sum(owner, -1)
        return utils.get_percentage_diff(curr, prev)

    def get_daily_expense_average(self, owner):
        expenses = self.get_user_expenses(owner).values("date", "amount")
        date_sum = {}
        for exp in expenses:
            date_sum[exp["date"]] = date_sum.get(exp["date"], 0) + exp["amount"]
        return round(sum(date_sum.values()) / len(date_sum), 2) if date_sum else 0

    def get_statistics(self, owner):
        return {
            "sum_expense": self.get_total_expenses(owner),
            "max_expense": self.get_max_expense(owner),
            "max_expense_content": self.get_max_expense_content(owner),
            "min_expense": self.get_min_expense(owner),
            "min_expense_content": self.get_min_expense_content(owner),
            "biggest_category_expenditure": self.get_biggest_category_expenditure(owner),
            "smallest_category_expenditure": self.get_smallest_category_expenditure(owner),
            "monthly_percentage_diff": self.get_curr_and_last_month_expenses_percentage_diff(owner),
            "monthly_expense_average": self.get_monthly_expense_average(owner),
            "daily_expense_average": self.get_daily_expense_average(owner),
            "curr_month_expense_sum": self.get_monthly_expense_sum(owner),
            "one_month_ago_expense_sum": self.get_monthly_expense_sum(owner, -1),
        }

    def get_budget(self, owner):
        budget = Budget.objects.filter(owner=owner).first()
        return budget.amount if budget else 0


class Expense(models.Model):
    amount = models.DecimalField(
        blank=False,
        default=10,
        decimal_places=2,
        max_digits=10,
        validators=[MinValueValidator(Decimal("0.01"))]
    )
    content = models.CharField(max_length=100, blank=False)

    CATEGORY_CHOICES = (
        ("Food & Groceries", "Food & Groceries"),
        ("Books & Stationery", "Books & Stationery"),
        ("Transportation", "Transportation"),
        ("Entertainment", "Entertainment"),
        ("Utilities", "Utilities"),
        ("Miscellaneous", "Miscellaneous"),
    )

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, null=True, blank=False)
    source = models.CharField(max_length=30, blank=False)
    date = models.DateTimeField(default=timezone.now, blank=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = ExpenseManager()

    def __str__(self):
        return f"{self.amount} on {self.content} ({self.category})"


class Budget(models.Model):
    amount = models.DecimalField(
        blank=False,
        default=0,
        decimal_places=2,
        max_digits=10,
        validators=[MinValueValidator(Decimal("0.01"))]
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Budget: {self.amount}"


import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from PIL import Image
import pytesseract
import requests


# Custom storage path for receipts
receipt_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'receipts'))

class ReceiptUpload(models.Model):
    image = models.ImageField(upload_to='receipts/', storage=receipt_storage)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    ocr_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Receipt uploaded by {self.owner.username} on {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} -> {self.user.username}"