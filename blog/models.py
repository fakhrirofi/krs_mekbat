from django.db import models
from django.utils import timezone

class Post(models.Model):
    title = models.CharField(max_length=50)
    author = models.CharField(max_length=20)
    date = models.DateField(default=timezone.now, blank=True)
    content = models.TextField(max_length=3000)

    def __str__(self):
        return self.title
