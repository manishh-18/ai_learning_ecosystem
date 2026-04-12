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
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
User = get_user_model()

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
        insight = ai_tutor_response(prompt)
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


@login_required
def instructor_dashboard(request):
    user = request.user

    courses = Course.objects.filter(instructor=user)

    enrollments = Enrollment.objects.filter(course__in=courses)

    quizzes = Quiz.objects.filter(created_by=user)

    attempts = QuizAttempt.objects.filter(quiz__created_by=user)

    total_students = enrollments.values('user').distinct().count()

    avg_score = 0
    if attempts.exists():
        avg_score = round(
            sum([(a.score / a.total) * 100 for a in attempts]) / attempts.count(), 2
        )

    context = {
        'courses': courses,
        'total_courses': courses.count(),
        'total_students': total_students,
        'total_quizzes': quizzes.count(),
        'avg_score': avg_score,
    }

    return render(request, 'instructor/dashboard.html', context)

def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


@login_required
def course_students(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollments = Enrollment.objects.filter(course=course)

    student_data = []

    for enroll in enrollments:
        student = enroll.user

        attempts = QuizAttempt.objects.filter(
            user=student,
            quiz__created_by=course.instructor
        )

        avg_score = 0
        if attempts.exists():
            avg_score = round(
                sum([(a.score / a.total) * 100 for a in attempts]) / attempts.count(), 2
            )

        student_data.append({
            'id': student.id,
            'name': student.full_name or student.username,
            'progress': enroll.progress,
            'avg_score': avg_score
        })

    # 🔥 TOP PERFORMER
    top_student = None
    if student_data:
        top_student = max(student_data, key=lambda x: x['avg_score'])

    # 🔥 WEAK STUDENTS
    weak_students = [s for s in student_data if s['avg_score'] < 50]

    return render(request, 'instructor/course_students.html', {
        'course': course,
        'students': student_data,
        'top_student': top_student,
        'weak_students': weak_students
    })


@login_required
def student_report(request, course_id, student_id):
    course = get_object_or_404(Course, id=course_id)
    student = get_object_or_404(User, id=student_id)

    enrollment = Enrollment.objects.filter(course=course, user=student).first()

    attempts = QuizAttempt.objects.filter(
        user=student,
        quiz__created_by=course.instructor
    )

    scores = []
    quiz_history = []

    for a in attempts:
        percent = round((a.score / a.total) * 100, 2) if a.total else 0
        scores.append(percent)

        quiz_history.append({
            'quiz': a.quiz.document.title if a.quiz.document else "Quiz",
            'score': percent
        })

    avg_score = round(sum(scores) / len(scores), 2) if scores else 0

    context = {
        'student': student,
        'course': course,
        'progress': enrollment.progress if enrollment else 0,
        'avg_score': avg_score,
        'scores': scores,
        'quiz_history': quiz_history
    }

    return render(request, 'instructor/student_report.html', context)