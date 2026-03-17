from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def student_dashboard(request):
    return render(request, 'student_dashboard.html')

def instructor_dashboard(request):
    return render(request, 'instructor_dashboard.html')

def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')