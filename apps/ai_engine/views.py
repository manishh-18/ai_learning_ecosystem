from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Chat, ChatSession
from .services.ai_service import ai_tutor_response
from django.views.decorators.csrf import csrf_exempt

@login_required
@csrf_exempt
def chat_view(request, session_id=None):

    # Get or create session
    if session_id:
        session = ChatSession.objects.get(id=session_id, user=request.user)
    else:
        session = ChatSession.objects.create(user=request.user)

    chats = Chat.objects.filter(session=session)

    # Sidebar sessions
    sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')

    if request.method == 'POST':
        question = request.POST.get('message')

        if question:
            answer = ai_tutor_response(question)

            Chat.objects.create(
                user=request.user,
                session=session,
                question=question,
                answer=answer
            )

    return render(request, 'ai_engine/chat.html', {
        'chats': chats,
        'sessions': sessions,
        'current_session': session
    })


