from django.shortcuts import render
from apps.courses.models import Course
from apps.documents.models import Document
from apps.assessments.models import Quiz
from django.contrib.auth.decorators import login_required
from apps.assessments.models import QuizAttempt
from apps.courses.models import Enrollment
import json

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


@login_required
def analytics_dashboard(request):
    user = request.user

    # 🔹 QUIZ ANALYTICS
    attempts = QuizAttempt.objects.filter(user=user)

    percentages = [
        (a.score / a.total) * 100 if a.total else 0
        for a in attempts
    ]

    avg_score = round(sum(percentages)/len(percentages), 2) if percentages else 0
    best_score = round(max(percentages), 2) if percentages else 0

    # 🔹 COURSE ANALYTICS
    enrollments = Enrollment.objects.filter(user=user)

    total_courses = enrollments.count()
    completed_courses = enrollments.filter(progress=100).count()

    avg_progress = round(
        sum([e.progress for e in enrollments]) / total_courses, 2
    ) if total_courses else 0

    # 🔹 AI INSIGHTS (SMART)
    if avg_score > 70:
        insight = "Great performance! You are doing well in quizzes."
    elif avg_score > 40:
        insight = "Good progress, but you can improve with more practice."
    else:
        insight = "Focus more on understanding concepts and revising topics."

    context = {
        'total_attempts': attempts.count(),
        'avg_score': avg_score,
        'best_score': best_score,
        'chart_data': json.dumps(percentages),

        'total_courses': total_courses,
        'completed_courses': completed_courses,
        'avg_progress': avg_progress,

        'insight': insight
    }

    return render(request, 'analytics/dashboard.html', context)