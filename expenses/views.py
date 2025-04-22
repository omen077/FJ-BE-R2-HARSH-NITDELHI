import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from expenses import utils
from expenses.utils import ExpenseGenerator

from .forms import BudgetForm, ExpenseForm, ReceiptUploadForm
from .models import Budget, Expense, ReceiptUpload, Notification

# Create your views here.

@login_required
def home(request):
    template = "homepage.html"
    all_expenses = Expense.objects.filter(owner=request.user).order_by('-date')
    
    # PAGINATION
    page = request.GET.get('page', 1)
    paginator = Paginator(all_expenses, 10)  # Show 10 expenses per page
    expenses = paginator.get_page(page)

    # Custom range for pagination (5 below and 5 above)
    current_page = expenses.number
    total_pages = paginator.num_pages
    pagination_range_down = max(current_page - 5, 1)
    pagination_range_up = min(current_page + 5, total_pages + 1)

    budget = Expense.objects.get_budget(request.user)
    statistics = Expense.objects.get_statistics(request.user)

    context = {
        "expenses": expenses,
        "budget": budget,
        "statistics": statistics,
        "num_pages": total_pages,
        "pagination_range_down": pagination_range_down,
        "pagination_range_up": pagination_range_up,
    }

    curr_expense = statistics["curr_month_expense_sum"]

    if budget:
        current_month_expenses = Expense.objects.get_monthly_expense_sum(
            owner=request.user
        )
        expenses_vs_budget_percentage_diff = (
            (current_month_expenses / budget * 100) if budget else 0
        )
        amount_over_budget = current_month_expenses - budget

        context["current_month_expenses"] = current_month_expenses
        context[
            "expenses_vs_budget_percentage_diff"
        ] = expenses_vs_budget_percentage_diff
        context["amount_over_budget"] = amount_over_budget

        if curr_expense < budget:
            context["is_over_budget"] = False
            context["is_under_budget"] = True
        else:
            context["is_over_budget"] = True
            context["is_under_budget"] = False
    return render(request, template, context)


@login_required
def homepage(request):
    # Add expenses to testuser to showcase expense and statistics tables
    # and charts.
    Expense.objects.add_testuser_expenses(request)

    template = "homepage.html"
    user_expenses = Expense.objects.filter(
        owner=request.user).order_by("-date")

    total_expense_amount = Expense.objects.get_total_expenses(
        owner=request.user)
    budget = Expense.objects.get_budget(owner=request.user)

    page = request.GET.get("page", 1)
    paginator = Paginator(user_expenses, 15)

    try:
        expenses = paginator.page(page)
    except PageNotAnInteger:
        expenses = paginator.page(1)
    except EmptyPage:
        expenses = paginator.page(paginator.num_pages)

    pagination_range_down = expenses.number - 5
    pagination_range_up = expenses.number + 5

    context = {
        "expenses": expenses,
        "total_expense_amount": total_expense_amount,
        "budget": budget,
        "num_expenses": len(user_expenses),
        "num_pages": paginator.num_pages,
        "pagination_range_down": pagination_range_down,
        "pagination_range_up": pagination_range_up,
    }

    if budget:
        current_month_expenses = Expense.objects.get_monthly_expense_sum(
            owner=request.user
        )
        expenses_vs_budget_percentage_diff = (
            (current_month_expenses / budget * 100) if budget else 0
        )
        amount_over_budget = current_month_expenses - budget

        context["current_month_expenses"] = current_month_expenses
        context[
            "expenses_vs_budget_percentage_diff"
        ] = expenses_vs_budget_percentage_diff
        context["amount_over_budget"] = amount_over_budget

    return render(request, template, context)


@login_required
def charts(request):
    template = "charts.html"
    expenses = Expense.objects.filter(owner=request.user)
    budget = Expense.objects.get_budget(request.user)
    statistics = Expense.objects.get_statistics(request.user)

    context = {"expenses": expenses,
               "budget": budget, "statistics": statistics}
    return render(request, template, context)


@login_required
def create_expense(request):
    template = "create_expense.html"

    if request.method != "POST":
        # No data submitted; create a blank form.
        form = ExpenseForm()
    else:
        # POST data submitted; process data.
        form = ExpenseForm(request.POST)
        if form.is_valid():
            new_expense = form.save(commit=False)
            new_expense.owner = request.user
            new_expense.save()
            return redirect("expenses:home")

    context = locals()
    return render(request, template, context)


@login_required
def view_expense(request, pk):
    template = "view_expense.html"
    expense = get_object_or_404(Expense, pk=pk)
    context = locals()

    return render(request, template, context)


@login_required
def update_expense(request, pk):
    template = "update_expense.html"
    expense = get_object_or_404(Expense, pk=pk)

    if request.method != "POST":
        form = ExpenseForm(instance=expense)

    else:
        form = ExpenseForm(instance=expense, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("expenses:home")

    context = locals()
    return render(request, template, context)


@login_required
def delete_expense(request, pk):
    template = "delete_expense.html"
    expense = get_object_or_404(Expense, pk=pk)

    if request.method == "POST":
        expense.delete()
        return redirect("expenses:home")

    return render(request, template, {})


@login_required
def create_budget(request):
    template = "create_budget.html"

    if request.method != "POST":
        # No data submitted; create a blank form.
        form = BudgetForm()
    else:
        # POST data submitted; process data.
        form = BudgetForm(request.POST)
        if form.is_valid():
            new_budget = form.save(commit=False)
            new_budget.owner = request.user
            new_budget.save()
            return redirect("expenses:home")

    context = locals()
    return render(request, template, context)


@login_required
def update_budget(request):
    template = "update_budget.html"
    budget = get_object_or_404(Budget, owner=request.user)

    if request.method != "POST":
        form = BudgetForm(instance=budget)

    else:
        form = BudgetForm(instance=budget, data=request.POST)
        if form.is_valid():
            updated_budget = form.save(commit=False)
            updated_budget.owner = request.user
            updated_budget.save()
            return redirect("expenses:home")

    context = locals()
    return render(request, template, context)


@login_required
def delete_budget(request):
    template = "delete_budget.html"
    budget = get_object_or_404(Budget, owner=request.user)

    if request.method == "POST":
        budget.delete()
        return redirect("expenses:home")

    return render(request, template, {})


@login_required
def view_404(request, exception):
    template = "errors/404.html"
    return render(request, template, {})


@login_required
def view_500(request):
    template = "errors/500.html"
    return render(request, template, {})


@login_required
def expense_table_data(request):
    user_expenses = Expense.objects.filter(owner=request.user)[:5]
    expenses_data = []

    for expense in user_expenses:
        new_expense = {
            'amount': float(expense.amount),
            'content': expense.content,
            'category': expense.category,
            'source': expense.source,
            'date': str(expense.date),

        }
        expenses_data.append(new_expense)

    return JsonResponse({'expenses': expenses_data})


@login_required
def statistics_table_data(request):
    statistics = Expense.objects.get_statistics(request.user)
    print(statistics['max_expense'].amount)
    stats = {
        "sum_expense": float(statistics['sum_expense']),
        'max_expense': float(statistics['max_expense'].amount),
        "max_expense_content": statistics['max_expense_content'],
        "min_expense": float(statistics['min_expense'].amount),
        "min_expense_content": statistics['min_expense_content'],
        "biggest_category_expenditure": statistics['biggest_category_expenditure'],
        "smallest_category_expenditure": statistics['smallest_category_expenditure'],
        "monthly_percentage_diff": float(statistics['monthly_percentage_diff']),
        "monthly_expense_average": float(statistics['monthly_expense_average']),
        "daily_expense_average": float(statistics['daily_expense_average']),
        "curr_month_expense_sum": float(statistics['curr_month_expense_sum']),
        "one_month_ago_expense_sum": float(statistics['one_month_ago_expense_sum']),
    }
    return JsonResponse(stats)


@login_required
def line_chart_data(request):
    user_expenses = Expense.objects.filter(owner=request.user)

    page = request.GET.get("page", 1)
    paginator = Paginator(user_expenses, 15)

    try:
        expenses = paginator.page(page)
    except PageNotAnInteger:
        expenses = paginator.page(1)
    except EmptyPage:
        expenses = paginator.page(paginator.num_pages)

    dates = [exp.date for exp in expenses]
    dates = [utils.reformat_date(date, "%d' %b") for date in dates]
    dates.reverse()

    amounts = [round(float(exp.amount), 2) for exp in expenses]
    amounts.reverse()

    chart_data = {}

    for i in range(len(dates)):
        if dates[i] not in chart_data:
            chart_data[dates[i]] = amounts[i]
        else:
            chart_data[dates[i]] += amounts[i]
    return JsonResponse(chart_data)


@login_required
def total_expenses_pie_chart_data(request):
    user_expenses = Expense.objects.filter(owner=request.user)

    chart_data = {}
    for exp in user_expenses:
        if exp.category not in chart_data:
            chart_data[exp.category] = float(exp.amount)
        else:
            chart_data[exp.category] += float(exp.amount)

    for category, amount in chart_data.items():
        chart_data[category] = round(amount, 2)
    return JsonResponse(chart_data)


@login_required
def monthly_expenses_pie_chart_data(request):
    user_expenses = Expense.objects.filter(owner=request.user)

    month_num = utils.get_month_num()
    monthly_expenses = user_expenses.filter(date__month=month_num)

    chart_data = {}
    for exp in monthly_expenses:
        if exp.category not in chart_data:
            chart_data[exp.category] = float(exp.amount)
        else:
            chart_data[exp.category] += float(exp.amount)

    for category, amount in chart_data.items():
        chart_data[category] = round(amount, 2)
    return JsonResponse(chart_data)


@login_required
def expenses_by_month_bar_chart_data(request):
    user_expenses = Expense.objects.filter(owner=request.user)
    current_year = utils.get_year_num()
    last_year = current_year - 1

    last_year_month_expenses = utils.get_yearly_month_expense_data(
        last_year, user_expenses
    )
    current_year_month_expenses = utils.get_yearly_month_expense_data(
        current_year, user_expenses
    )
    chart_data = {**last_year_month_expenses, **current_year_month_expenses}
    return JsonResponse(chart_data)


@login_required
def expenses_by_week_bar_chart_data(request):
    weeks = ["current week", "last week", "2 weeks ago", "3 weeks ago"]
    weeks.reverse()

    expenses = [
        Expense.objects.get_weekly_expense_sum(request.user),
        Expense.objects.get_weekly_expense_sum(request.user, -1),
        Expense.objects.get_weekly_expense_sum(request.user, -2),
        Expense.objects.get_weekly_expense_sum(request.user, -3),
    ]
    expenses.reverse()

    chart_data = {}
    for i, week in enumerate(weeks):
        chart_data[week] = expenses[i]
    return JsonResponse(chart_data)


@login_required
def add_testuser_data(request):
    user = str(request.user)
    if user == "testuser1" or user == "testuser3":
        req_post_dict = dict(request.POST)
        expenses_str_dict = req_post_dict["expenses"][0]
        expenses = json.loads(expenses_str_dict)

        Expense.objects.create_test_expenses(request.user, expenses)
        return redirect("expenses:home")


@login_required
def delete_testuser_data(request):
    """Function to remove all data from testusers that can be access via url by tests."""
    user = str(request.user)

    if user == "testuser1" or user == "testuser3":
        Expense.objects.delete_testuser_expenses(request)
        Expense.objects.delete_testuser_budget(request)

        testusers_to_delete = User.objects.exclude(username="testuser1").exclude(
            username="testuser3"
        )
        testusers_to_delete.delete()

        return redirect("expenses:home")
    else:
        print(
            "Not allowed to delete the expenses or budget of any user other than testuser1 and testuser3"
        )
        return redirect("expenses:home")


# views.py

@login_required
def user_notifications(request):
    """View all user notifications with pagination"""
    notifications = request.user.notifications.order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(notifications, 10)  # Show 10 notifications per page
    
    try:
        paginated_notifications = paginator.page(page)
    except PageNotAnInteger:
        paginated_notifications = paginator.page(1)
    except EmptyPage:
        paginated_notifications = paginator.page(paginator.num_pages)
    
    context = {
        "notifications": paginated_notifications,
        "unread_count": unread_count,
        "num_pages": paginator.num_pages,
    }
    
    return render(request, "notifications/list.html", context)


@login_required
def mark_notification_as_read(request, notification_id):
    """Mark a notification as read"""
    from .models import Notification
    
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # If it's an AJAX request, return JSON response
        return JsonResponse({"status": "success"})
    
    # Otherwise redirect back to notifications
    return redirect("expenses:user_notifications")


@login_required
def mark_all_notifications_as_read(request):
    """Mark all notifications as read"""
    request.user.notifications.update(is_read=True)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # If it's an AJAX request, return JSON response
        return JsonResponse({"status": "success"})
    
    # Otherwise redirect back to notifications
    return redirect("expenses:user_notifications")


@login_required
def import_data_from_json(request):
    """Imports expense data from either a file or direct JSON input"""
    if request.method == "POST":
        import_type = request.POST.get('import_type', 'file')
        
        try:
            # Get data from either file or direct input
            if import_type == 'direct':
                json_data = request.POST.get('json_data', '')
                if not json_data.strip():
                    messages.error(request, "No JSON data provided")
                    return render(request, "import_data.html")
                
                try:
                    expenses_by_date = json.loads(json_data)
                except json.JSONDecodeError:
                    messages.error(request, "Invalid JSON format in provided data")
                    return render(request, "import_data.html")
            else:
                # Import from file
                try:
                    with open('expenses/data.json') as f:
                        expenses_by_date = json.load(f)
                except FileNotFoundError:
                    messages.error(request, "File expenses/data.json not found")
                    return render(request, "import_data.html")
                except json.JSONDecodeError:
                    messages.error(request, "Invalid JSON format in expenses/data.json")
                    return render(request, "import_data.html")
            
            # Use the ExpenseGenerator to generate expenses with proper dates
            try:
                expense_generator = ExpenseGenerator(expenses_by_date)
                expenses_data = expense_generator.generate_expenses()
            except Exception as e:
                messages.error(request, f"Error generating expenses: {str(e)}")
                return render(request, "import_data.html")
            
            # Map non-standard categories to standard ones if needed
            category_mapping = {
                'Monthly bill': 'Utilities',
                'Bar tabs': 'Entertainment',
                'Online shopping': 'Miscellaneous', 
                'Groceries': 'Food & Groceries',
                'Taxi fare': 'Transportation',
                'Electronics': 'Miscellaneous'
            }
            
            # Create the expenses
            counter = 0
            for expense_data in expenses_data:
                # Map category if needed
                category = expense_data.get('category', 'Miscellaneous')
                if category in category_mapping:
                    mapped_category = category_mapping[category]
                else:
                    mapped_category = 'Miscellaneous'
                
                try:
                    expense = Expense(
                        amount=expense_data['amount'],
                        content=expense_data['content'],
                        category=mapped_category,
                        source=expense_data['source'],
                        date=expense_data['date'],
                        owner=request.user
                    )
                    expense.save()
                    counter += 1
                except Exception as e:
                    messages.warning(request, f"Skipped one expense: {str(e)}")
                    continue
            
            if counter > 0:
                messages.success(request, f"Successfully imported {counter} expenses")
                return redirect("expenses:home")
            else:
                messages.error(request, "No valid expenses found to import")
                
        except Exception as e:
            messages.error(request, f"Error importing data: {str(e)}")
    
    return render(request, "import_data.html")


@login_required
def notification_detail(request, notification_id):
    """View a single notification in detail"""
    from .models import Notification
    
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    # Mark as read when viewed
    if not notification.is_read:
        notification.is_read = True
        notification.save()
    
    context = {
        "notification": notification
    }
    
    return render(request, "notifications/detail.html", context)


@login_required
def export_data(request):
    """View for the export data page where users can select export options"""
    return render(request, 'expenses/export_data.html')

@login_required
def export_data_file(request):
    """Handle the export data request and generate the appropriate file"""
    if request.method != 'POST':
        return redirect('expenses:export_data')
    
    export_format = request.POST.get('export_format')
    time_period = request.POST.get('time_period')
    
    if not export_format or not time_period:
        messages.error(request, 'Please select both a format and time period for export')
        return redirect('expenses:export_data')
    
    # Get expenses based on the selected time period
    from expenses.utils import get_user_expenses_for_export
    expenses = get_user_expenses_for_export(request.user, time_period)
    
    # Generate file based on selected format
    from django.http import HttpResponse
    
    if export_format == 'csv':
        from expenses.utils import export_expenses_to_csv
        
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="expenses_{time_period}.csv"'},
        )
        
        response.write(export_expenses_to_csv(expenses))
        return response
    
    elif export_format == 'json':
        from expenses.utils import export_expenses_to_json
        
        response = HttpResponse(
            content_type='application/json',
            headers={'Content-Disposition': f'attachment; filename="expenses_{time_period}.json"'},
        )
        
        response.write(export_expenses_to_json(expenses))
        return response
    
    elif export_format == 'pdf':
        from expenses.utils import export_expenses_to_pdf
        
        response = HttpResponse(
            content_type='application/pdf',
            headers={'Content-Disposition': f'attachment; filename="expenses_{time_period}.pdf"'},
        )
        
        pdf_data = export_expenses_to_pdf(expenses, request.user, time_period)
        
        if pdf_data:
            response.write(pdf_data)
            return response
        else:
            messages.error(request, 'Error generating PDF file')
            return redirect('expenses:export_data')
    
    # Default case - invalid format
    messages.error(request, 'Invalid export format')
    return redirect('expenses:export_data')

@login_required
def upload_receipt(request):
    """
    View for handling receipt uploads
    """
    if request.method == "POST":
        form = ReceiptUploadForm(request.POST, request.FILES)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.owner = request.user
            
            # Save the receipt
            receipt.save()
            
            # Create a notification about the successful upload
            Notification.objects.create(
                user=request.user,
                title="Receipt Uploaded",
                message="Your receipt has been successfully uploaded and is being processed."
            )
            
            messages.success(request, "Receipt uploaded successfully!")
            return redirect("expenses:receipt_list")
    else:
        form = ReceiptUploadForm()
    
    return render(request, "expenses/upload_receipt.html", {"form": form})

@login_required
def receipt_list(request):
    """
    View for displaying all receipts uploaded by the user
    """
    receipts = ReceiptUpload.objects.filter(owner=request.user).order_by('-uploaded_at')
    return render(request, "expenses/receipt_list.html", {"receipts": receipts})

@login_required
def receipt_detail(request, receipt_id):
    """
    View for displaying details of a specific receipt
    """
    receipt = get_object_or_404(ReceiptUpload, id=receipt_id, owner=request.user)
    return render(request, "expenses/receipt_detail.html", {"receipt": receipt})

@login_required
def delete_receipt(request, receipt_id):
    """
    View for deleting a receipt
    """
    receipt = get_object_or_404(ReceiptUpload, id=receipt_id, owner=request.user)
    
    if request.method == "POST":
        # Delete the receipt
        receipt.delete()
        
        # Create a notification about the deletion
        Notification.objects.create(
            user=request.user,
            title="Receipt Deleted",
            message=f"Receipt #{receipt_id} has been successfully deleted."
        )
        
        messages.success(request, "Receipt deleted successfully!")
        return redirect("expenses:receipt_list")
    
    # If method is GET, just show the receipt detail (never directly delete on GET)
    return redirect("expenses:receipt_detail", receipt_id=receipt_id)
