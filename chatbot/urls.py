from django.urls import path
from . import views

urlpatterns = [
    path('api/', views.chatbot_api, name='chatbot_api'),
    path('widget/', views.chatbot_widget, name='chatbot_widget'),
    path('history/', views.chatbot_history, name='chatbot_history'),
    path('toggle-ai/', views.toggle_ai_mode, name='toggle_ai_mode'),
    path('delete-session/<str:session_id>/', views.delete_chat_session, name='delete_chat_session'),
    path('clear-history/', views.clear_chat_history, name='clear_chat_history'),
]
