from django.urls import path
from .views import generate_quiz, view_quiz

urlpatterns = [
    path('generate/<int:doc_id>/', generate_quiz, name='generate_quiz'),
    path('view/<int:quiz_id>/', view_quiz, name='view_quiz'),
]