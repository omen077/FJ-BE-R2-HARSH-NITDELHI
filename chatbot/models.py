from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    MESSAGE_TYPES = (
        ('user', 'User Message'),
        ('system', 'System Message'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"
