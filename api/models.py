from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Document(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    answer_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.question_text[:50]}..."
    
file = models.FileField(upload_to='documents/')

