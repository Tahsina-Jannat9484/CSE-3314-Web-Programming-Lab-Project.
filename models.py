from django.db import models
from django.contrib.auth.models import User
import json


class CSVUpload(models.Model):
    """Model to store uploaded CSV file information"""
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='csv_uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    processed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.uploaded_at}"

    class Meta:
        ordering = ['-uploaded_at']


class CSVRecord(models.Model):
    """Model to store individual CSV records"""
    csv_upload = models.ForeignKey(CSVUpload, on_delete=models.CASCADE, related_name='records')
    data = models.JSONField()  # Store the row data as JSON
    score = models.FloatField(default=0.0)  # For ranking purposes
    rank = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Record {self.id} - Score: {self.score}"
    
    class Meta:
        ordering = ['-score']


class ChatSession(models.Model):
    """Model to store chat sessions with Ollama"""
    csv_upload = models.ForeignKey(CSVUpload, on_delete=models.CASCADE, related_name='chat_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Chat Session {self.session_id}"


class ChatMessage(models.Model):
    """Model to store chat messages"""
    MESSAGE_TYPES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
    )
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."
    
    class Meta:
        ordering = ['timestamp']
