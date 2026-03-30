from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Chat
from .services.ai_service import ai_tutor_response
from django.views.decorators.csrf import csrf_exempt

@login_required
@csrf_exempt
def chat_view(request):
    chats = Chat.objects.filter(user=request.user).order_by('created_at')

    if request.method == 'POST':
        question = request.POST.get('message')

        if not question:
            return redirect('chat')

        answer = ai_tutor_response(question)

        Chat.objects.create(
            user=request.user,
            question=question,
            answer=answer
        )

        return redirect('chat')   # ✅ IMPORTANT

    return render(request, 'ai_engine/chat.html', {'chats': chats})