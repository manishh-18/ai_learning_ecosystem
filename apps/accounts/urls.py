from django.urls import path
from .views import register_view, login_view, logout_view, dashboard_redirect

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('redirect/', dashboard_redirect, name='dashboard_redirect'),
]