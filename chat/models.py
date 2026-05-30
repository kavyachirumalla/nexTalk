from django.db import models

# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)
    users = models.ManyToManyField('auth.User', related_name='rooms')
    def __str__(self):
        return self.name
class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    file=models.FileField(upload_to='chat_files/', null=True, blank=True)
    image=models.ImageField(upload_to='chat_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.sender}: {self.content[:20]}..."