from django.db import models
from django.conf import settings
from apps.documents.models import Document

User = settings.AUTH_USER_MODEL

class Quiz(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    questions = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz for {self.document.title}"