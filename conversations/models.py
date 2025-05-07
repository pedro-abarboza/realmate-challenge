from django.db import models
import uuid

class Conversation(models.Model):
    CONVERSATION_STATUS = (
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=10, choices=CONVERSATION_STATUS, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Conversation {self.id} - {self.status}"
    
    class Meta:
        ordering = ['-updated_at']


class Message(models.Model):
    MESSAGE_DIRECTIONS = (
        ('SENT', 'Sent'),
        ('RECEIVED', 'Received'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, 
        related_name='messages', 
        on_delete=models.CASCADE
    )
    direction = models.CharField(max_length=10, choices=MESSAGE_DIRECTIONS)
    content = models.TextField()
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message {self.id} ({self.direction}) - {self.conversation.id}"
    
    class Meta:
        ordering = ['timestamp']
