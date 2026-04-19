from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.documents.models import Document
from apps.ai_engine.services.ai_service import generate_questions
from apps.ai_engine.services.ai_service import generate_feedback
from .models import Quiz, Course
from apps.courses.models import Enrollment
from .models import QuizAttempt
from django.db.models import Max


@login_required
def quiz_list(request):

    # ✅ ROLE-BASED FILTER
    if request.user.role == 'instructor':
        quizzes = Quiz.objects.filter(created_by=request.user)
    else:
        enrolled_courses = Enrollment.objects.filter(user=request.user).values_list('course', flat=True)
        quizzes = Quiz.objects.filter(course__in=enrolled_courses)

    attempts = QuizAttempt.objects.filter(user=request.user)

    quiz_data = []

    for quiz in quizzes:
        latest_attempt = None

        for attempt in attempts:
            if attempt.quiz.id == quiz.id:
                latest_attempt = attempt

        quiz_data.append({
            'quiz': quiz,
            'attempt': latest_attempt
        })

    return render(request, 'assessments/quiz_list.html', {
        'quiz_data': quiz_data
    })


@login_required
@login_required
def view_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        results = []
        score = 0

        for i, q in enumerate(quiz.questions, start=1):
            selected = request.POST.get(f'q{i}')

            if not selected:
                selected = "Not Answered"

            correct = q['correct_answer']

            # ✅ FIX: compare only option letter (A, B, C, D)
            selected_clean = selected.strip().upper()[0] if selected != "Not Answered" else ""
            correct_clean = correct.strip().upper()[0]

            if selected_clean == correct_clean:
                score += 1
                results.append({
                    'question': q['question'],
                    'result': 'Correct'
                })
            else:
                feedback = generate_feedback(
                    question=q['question'],
                    selected_answer=selected,
                    correct_answer=correct,
                    explanation=q.get('explanation', '')
                )
                results.append({
                    'question': q['question'],
                    'result': 'Wrong',
                    'selected': selected,
                    'correct': correct,
                    'feedback': feedback
                })

        # ✅ FIX: create attempt ONLY ONCE (outside loop)
        QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            total=len(quiz.questions)
        )

        return render(request, 'assessments/result.html', {
            'results': results,
            'score': score,
            'total': len(quiz.questions)
        })

    return render(request, 'assessments/view_quiz.html', {'quiz': quiz})

@login_required
def generate_quiz_page(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)

    context = {'document': document}

    if request.user.role == 'instructor':
        context['courses'] = Course.objects.filter(instructor=request.user)

    return render(request, 'assessments/generate.html', context)

@login_required
def generate_quiz(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)

    questions = generate_questions(document.extracted_text[:3000])

    # ✅ STUDENT FLOW
    if request.user.role == 'student':
        quiz = Quiz.objects.create(
            document=document,
            created_by=request.user,
            questions=questions,
            course=None   # ✅ VERY IMPORTANT
        )
        print("TEXT:", document.extracted_text[:200])
        print("QUESTIONS:", questions)
        return redirect('view_quiz', quiz_id=quiz.id)

    # ✅ INSTRUCTOR FLOW
    if request.user.role == 'instructor':

        if request.method == 'POST':
            course_id = request.POST.get('course_id')

            if not course_id:
                return redirect('generate_quiz_page', doc_id=doc_id)

            course = get_object_or_404(Course, id=course_id)

            quiz = Quiz.objects.create(
                document=document,
                created_by=request.user,
                questions=questions,
                course=course
            )
            return redirect('instructor_dashboard')
        # 🔥 FIXED HERE
        return redirect('generate_quiz_page', doc_id=doc_id)

@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    quiz.delete()
    return redirect('quiz_list')
