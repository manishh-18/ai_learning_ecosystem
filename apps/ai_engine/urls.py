from django.urls import path
from .views import chat_view

urlpatterns = [
    path('chat/', chat_view, name='chat'),
    path('chat/<int:session_id>/', chat_view, name='chat_session'),
]