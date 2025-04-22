from django.urls import path, re_path

from expenses import views

app_name = "expenses"

urlpatterns = [
    path("", views.home, name="home"),
    # re_path(r'^(?:.*)/?$', views.home)

    path("", views.homepage, name="home"),
    path("charts/", views.charts, name="charts"),
    path("create/", views.create_expense, name="create"),
    path("update/<int:pk>/", views.update_expense, name="update"),
    path("delete/<int:pk>/", views.delete_expense, name="delete"),
    path("create-budget/", views.create_budget, name="create_budget"),
    path("update-budget/", views.update_budget, name="update_budget"),
    path("delete-budget/", views.delete_budget, name="delete_budget"),
    # TEMP URLS
    path("expense-table-data/", views.expense_table_data, name="expense_table_data"),       # get list of expenses in json format
    path("statistics-table-data/", views.statistics_table_data, name="statistics_table_data"),       # get list of statistics in json format        
    # END TEMP URLS
    path("line-chart-data/", views.line_chart_data, name="line_chart_data"),
    path(
        "total-expenses-pie-chart-data/",
        views.total_expenses_pie_chart_data,
        name="total_expenses_pie_chart_data",
    ),
    path(
        "monthly-expenses-pie-chart-data/",
        views.monthly_expenses_pie_chart_data,
        name="monthly_expenses_pie_chart_data",
    ),
    path(
        "expenses-by-month-bar-chart-data/",
        views.expenses_by_month_bar_chart_data,
        name="expenses_by_month_bar_chart_data",
    ),
    path(
        "expenses-by-week-bar-chart-data/",
        views.expenses_by_week_bar_chart_data,
        name="expenses_by_week_bar_chart_data",
    ),
    path("add-testuser-data/", views.add_testuser_data, name="add_testuser_data"),
    path(
        "delete-testuser-data/", views.delete_testuser_data, name="delete_testuser_data"
    ),
    path("import-data/", views.import_data_from_json, name="import_data"),
    path("notifications/", views.user_notifications, name="user_notifications"),  
    path("notifications/<int:notification_id>/", views.notification_detail, name="notification_detail"),
    path("notifications/mark-read/<int:notification_id>/", views.mark_notification_as_read, name="mark_notification_as_read"),
    path("notifications/mark-all-read/", views.mark_all_notifications_as_read, name="mark_all_notifications_as_read"),
    
    # Export data URLs
    path("export-data/", views.export_data, name="export_data"),
    path("export-data/file/", views.export_data_file, name="export_data_file"),
    
    # Receipt URLs
    path("receipts/upload/", views.upload_receipt, name="upload_receipt"),
    path("receipts/", views.receipt_list, name="receipt_list"),
    path("receipts/<int:receipt_id>/", views.receipt_detail, name="receipt_detail"),
    path("receipts/<int:receipt_id>/delete/", views.delete_receipt, name="delete_receipt"),
]
