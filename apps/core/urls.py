from django.urls import path
from .views import home, student_dashboard, instructor_dashboard, admin_dashboard, course_students, student_report

urlpatterns = [
    path('', home, name='home'),
    path('student/', student_dashboard, name='student_dashboard'),
    path('instructor/', instructor_dashboard, name='instructor_dashboard'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('course/<int:course_id>/students/', course_students, name='course_students'),
    path('course/<int:course_id>/student/<int:student_id>/', student_report, name='student_report'),
]