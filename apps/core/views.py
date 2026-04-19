from django.shortcuts import render, redirect
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

    # 🔹 Topic analysis (UPDATED)
    topic_avg = {t: round(sum(v)/len(v), 2) for t, v in topic_scores.items()}

    # ✅ FIXED: meaningful strong & weak topics
    strong_topics = sorted(topic_avg, key=topic_avg.get, reverse=True)[:3]
    weak_topics = sorted(topic_avg, key=topic_avg.get)[:3]

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
    # 🔹 AI Insight (STATIC — button will handle real AI)
    insight = "Click 'Generate Insight' to analyze your performance."

    # ✅ FIXED: topic-based chart instead of attempts
    chart_labels = []
    chart_values = []
    chart_topics = []

    for i, a in enumerate(attempts, start=1):
        percent = (a.score / a.total) * 100 if a.total else 0
        topic = a.quiz.document.title

        chart_labels.append(f"Attempt {i}")
        chart_values.append(percent)
        chart_topics.append(topic)

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

        # UPDATED CHART DATA
        'chart_labels': json.dumps(chart_labels),
        'chart_values': json.dumps(chart_values),
        'chart_topics': json.dumps(chart_topics),

        'insight': insight
    }

    return render(request, 'analytics/dashboard.html', context)


@login_required
def instructor_dashboard(request):
    user = request.user

    courses = Course.objects.filter(instructor=user)

    enrollments = Enrollment.objects.filter(course__in=courses)
    quizzes = Quiz.objects.filter(created_by=request.user)
    attempts = QuizAttempt.objects.filter(quiz__course__in=courses)

    total_students = enrollments.values('user').distinct().count()

    avg_score = 0
    if attempts.exists():
        avg_score = round(
            sum([(a.score / a.total) * 100 for a in attempts]) / attempts.count(), 2
        )

    # ✅ Course-wise analytics
    course_data = []
    for course in courses:
        course_enrollments = Enrollment.objects.filter(course=course)
        course_students = course_enrollments.count()

        course_attempts = QuizAttempt.objects.filter(quiz__course=course)

        course_avg = 0
        if course_attempts.exists():
            course_avg = round(
                sum([(a.score / a.total) * 100 for a in course_attempts]) / course_attempts.count(), 2
            )

        course_data.append({
            'course': course,
            'students': course_students,
            'avg_score': course_avg
        })

    context = {
        'courses': courses,
        'course_data': course_data,
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

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import markdown

@login_required
@csrf_exempt
def generate_ai_insight(request):
    if request.method == "POST":
        try:
            user = request.user

            attempts = QuizAttempt.objects.filter(user=user).select_related('quiz__document')

            topic_scores = defaultdict(list)

            for a in attempts:
                percent = (a.score / a.total) * 100 if a.total else 0
                topic = a.quiz.document.title
                topic_scores[topic].append(percent)

            topic_avg = {t: round(sum(v)/len(v), 2) for t, v in topic_scores.items()}

            strong_topics = sorted(topic_avg, key=topic_avg.get, reverse=True)[:3]
            weak_topics = sorted(topic_avg, key=topic_avg.get)[:3]

            scores = []

            for a in attempts:
                if a.total:  # avoid division by zero
                    percent = (a.score / a.total) * 100 if a.total else 0
                    scores.append(percent)

            avg_score = round(sum(scores) / len(scores), 2) if scores else 0

            prompt = f"""
            Student performance:

            Avg Score: {avg_score}
            Weak Topics: {weak_topics}
            Strong Topics: {strong_topics}

            Give short improvement advice in 3-4 lines.
            """

            insight = ai_tutor_response(prompt)
            insight = markdown.markdown(
                insight,
                extensions=['extra', 'nl2br']
            )

            return JsonResponse({'insight': insight})

        except Exception as e:
            print("AI ERROR:", e) 
            return JsonResponse({'insight': 'Unable to generate insight right now.'})