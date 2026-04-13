from django.db import models
from django.conf import settings
from apps.documents.models import Document

User = settings.AUTH_USER_MODEL

from apps.courses.models import Course

class Quiz(models.Model):
    document = models.ForeignKey('documents.Document', on_delete=models.CASCADE)
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    questions = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz for {self.document.title}"
    
class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    total = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.score}/{self.total}"