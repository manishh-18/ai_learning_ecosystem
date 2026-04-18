from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Chat, ChatSession
from .services.ai_service import ai_tutor_response
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import markdown   # ✅ ADD THIS

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
            raw_answer = ai_tutor_response(question)

            # ✅ CONVERT TO HTML (MARKDOWN)
            answer = markdown.markdown(raw_answer)

            # ✅ Set title from first question
            if session.title == "New Chat":
                session.title = question[:40]
                session.save()

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


@login_required
def delete_chat_session(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    session.delete()
    return redirect('chat')


@login_required
def rename_chat_session(request, session_id):
    if request.method == "POST":
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        new_title = request.POST.get("title")

        if new_title:
            session.title = new_title
            session.save()
            return JsonResponse({"success": True})

    return JsonResponse({"success": False})


@login_required
def delete_multiple_chats(request):
    if request.method == "POST":
        ids = request.POST.getlist("session_ids[]")

        ChatSession.objects.filter(id__in=ids, user=request.user).delete()

    return redirect('chat')