from django.shortcuts import render
from apps.courses.models import Course
from apps.documents.models import Document
from apps.assessments.models import Quiz
from django.contrib.auth.decorators import login_required
from apps.assessments.models import QuizAttempt
from apps.courses.models import Enrollment
import json
from collections import defaultdict
from apps.ai_engine.services.ai_service import ai_tutor_response


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

    attempts = QuizAttempt.objects.filter(user=user).select_related('quiz__document')

    topic_scores = defaultdict(list)
    percentages = []

    for a in attempts:
        percent = (a.score / a.total) * 100 if a.total else 0
        percentages.append(percent)

        topic = a.quiz.document.title
        topic_scores[topic].append(percent)

    # 🔹 Topic analysis
    topic_avg = {t: round(sum(v)/len(v), 2) for t, v in topic_scores.items()}
    weak_topics = [t for t, v in topic_avg.items() if v < 50]
    strong_topics = [t for t, v in topic_avg.items() if v > 75]

    # 🔹 Quiz stats
    total_quizzes = attempts.count()
    avg_score = round(sum(percentages)/len(percentages), 2) if percentages else 0
    best_score = round(max(percentages), 2) if percentages else 0

    # 🔹 Recent performance (last 5)
    recent_attempts = percentages[-5:]
    improvement = "Stable"

    if len(recent_attempts) >= 2:
        if recent_attempts[-1] > recent_attempts[0]:
            improvement = "Improving 📈"
        elif recent_attempts[-1] < recent_attempts[0]:
            improvement = "Declining 📉"

    # 🔹 Course analytics
    enrollments = Enrollment.objects.filter(user=user)
    total_courses = enrollments.count()
    completed_courses = enrollments.filter(progress=100).count()

    avg_progress = round(
        sum([e.progress for e in enrollments]) / total_courses, 2
    ) if total_courses else 0

    # 🔹 AI Insight
    prompt = f"""
    Student performance:

    Avg Score: {avg_score}
    Weak Topics: {weak_topics}
    Strong Topics: {strong_topics}
    Recent Trend: {improvement}

    Give short improvement advice in 2 lines.
    """

    try:
        insight = ai_tutor_response(prompt).text.strip()
    except:
        insight = "Focus on weak topics and practice regularly."

    context = {
        'total_quizzes': total_quizzes,
        'avg_score': avg_score,
        'best_score': best_score,
        'improvement': improvement,

        'total_courses': total_courses,
        'completed_courses': completed_courses,
        'avg_progress': avg_progress,

        'topic_avg': topic_avg,
        'weak_topics': weak_topics,
        'strong_topics': strong_topics,

        'chart_data': json.dumps(percentages),
        'insight': insight
    }

    return render(request, 'analytics/dashboard.html', context)