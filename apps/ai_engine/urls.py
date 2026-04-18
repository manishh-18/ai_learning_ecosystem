from django.urls import path
from .views import chat_view, delete_chat_session, rename_chat_session, delete_multiple_chats

urlpatterns = [
    path('chat/', chat_view, name='chat'),
    path('chat/<int:session_id>/', chat_view, name='chat_session'),
    path('chat/delete/<int:session_id>/', delete_chat_session, name='delete_chat'),
    path('chat/rename/<int:session_id>/', rename_chat_session, name='rename_chat'),
    path('chat/delete-multiple/', delete_multiple_chats, name='delete_multiple_chats'),
]