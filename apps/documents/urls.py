from django.urls import path
from .views import upload_document, document_list,view_summary

urlpatterns = [
    path('upload/', upload_document, name='upload_document'),
    path('list/', document_list, name='document_list'),
    path('summary/<int:doc_id>/', view_summary, name='view_summary'),
]