from django.urls import path
from .views import create_course, course_list, enroll_course, course_detail, manage_course, add_material,add_video

urlpatterns = [
    path('create/', create_course, name='create_course'),
    path('list/', course_list, name='course_list'),
    path('enroll/<int:course_id>/', enroll_course, name='enroll_course'),
    path('<int:course_id>/', course_detail, name='course_detail'),
    path('manage/<int:course_id>/', manage_course, name='manage_course'),
    path('add-material/<int:course_id>/', add_material, name='add_material'),
    path('add-video/<int:course_id>/', add_video, name='add_video'),
]