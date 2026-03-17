from django.urls import path
from .views import create_course, course_list

urlpatterns = [
    path('create/', create_course, name='create_course'),
    path('list/', course_list, name='course_list'),
]