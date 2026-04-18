from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.documents.models import Document
from apps.ai_engine.services.ai_service import generate_questions
from apps.ai_engine.services.ai_service import generate_feedback
from .models import Quiz, Course
from .models import QuizAttempt
from django.db.models import Max


@login_required
def quiz_list(request):
    quizzes = Quiz.objects.all()
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

            if selected == correct:
                score += 1
                results.append({
                    'question': q['question'],
                    'result': 'Correct'
                })
            else:
                feedback = generate_feedback(
                    question=q['question'],
                    selected_answer=selected,
                    correct_answer=q['correct_answer'],
                    explanation=q.get('explanation', '')
                )
                results.append({
                    'question': q['question'],
                    'result': 'Wrong',
                    'selected': selected,
                    'correct': correct,
                    'feedback': feedback
                })
            QuizAttempt.objects.create(
                user=request.user,
                quiz=quiz,
                score=score,
                total=len(quiz.questions)
            )

            print("RESULTS:", results)
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

    return render(request, 'assessments/generate.html', {
        'document': document
    })

@login_required
def generate_quiz(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)

    courses = Course.objects.filter(instructor=request.user)

    if request.method == 'POST':
        course_id = request.POST.get('course')
        course = Course.objects.get(id=course_id)

        questions = generate_questions(document.extracted_text[:3000])

        quiz = Quiz.objects.create(
            document=document,
            created_by=request.user,
            course=course,
            questions=questions
        )

        return redirect('view_quiz', quiz_id=quiz.id)

    return render(request, 'assessments/select_course.html', {
        'document': document,
        'courses': courses
    })

@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    quiz.delete()
    return redirect('quiz_list')
