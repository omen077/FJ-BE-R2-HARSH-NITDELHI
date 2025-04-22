from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chat_history, name='chat_history'),
    path('process/', views.process_message, name='process_message'),
    path('docs/', views.documentation, name='documentation'),
] 