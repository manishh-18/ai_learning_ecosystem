from django.shortcuts import render
from apps.courses.models import Course
from apps.documents.models import Document
from apps.assessments.models import Quiz
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')

@login_required
def student_dashboard(request):
    user = request.user

    context = {
        'name': user.full_name,
        'course_count': Course.objects.count(),
        'doc_count': Document.objects.filter(uploaded_by=user).count(),
        'quiz_count': Quiz.objects.filter(created_by=user).count(),
    }

    return render(request, 'student_dashboard.html', context)

def instructor_dashboard(request):
    return render(request, 'instructor_dashboard.html')

def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')