from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    room = models.CharField(max_length=250)
    user = models.ForeignKey(User,
            related_name='user_message',
            on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    message = models.TextField(null=True)
    image = models.ImageField(null=True)
    
    class Meta:
        ordering = ['-created']


    
