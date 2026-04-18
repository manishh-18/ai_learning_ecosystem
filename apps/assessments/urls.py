from django.urls import path
from .views import generate_quiz, view_quiz, quiz_list, delete_quiz, generate_quiz_page

urlpatterns = [
    path('generate/<int:doc_id>/', generate_quiz, name='generate_quiz'),
    path('generate-page/<int:doc_id>/', generate_quiz_page, name='generate_quiz_page'),
    path('view/<int:quiz_id>/', view_quiz, name='view_quiz'),
    path('list/', quiz_list, name='quiz_list'),
    path('delete/<int:quiz_id>/', delete_quiz, name='delete_quiz'),
]