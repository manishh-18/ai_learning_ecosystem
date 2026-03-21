from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.documents.models import Document
from apps.ai_engine.services.ai_service import generate_questions
from apps.ai_engine.services.ai_service import generate_feedback
from .models import Quiz


@login_required
def generate_quiz(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)

    questions = generate_questions(document.extracted_text[:3000])

    quiz = Quiz.objects.create(
        document=document,
        created_by=request.user,
        questions=questions
    )

    return redirect('view_quiz', quiz_id=quiz.id)


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

            print("RESULTS:", results)

        return render(request, 'assessments/result.html', {
            'results': results,
            'score': score,
            'total': len(quiz.questions)
        })

    return render(request, 'assessments/view_quiz.html', {'quiz': quiz})