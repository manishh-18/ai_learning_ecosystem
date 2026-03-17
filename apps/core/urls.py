from django.urls import path
from .views import home, student_dashboard, instructor_dashboard, admin_dashboard

urlpatterns = [
    path('', home, name='home'),
    path('student/', student_dashboard, name='student_dashboard'),
    path('instructor/', instructor_dashboard, name='instructor_dashboard'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
]