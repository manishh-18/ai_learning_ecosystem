from django.urls import path
from .views import upload_document, document_list

urlpatterns = [
    path('upload/', upload_document, name='upload_document'),
    path('list/', document_list, name='document_list'),
]