from django.db import models
from django.conf import settings

# Create your models here.


class Image(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    query_text = models.TextField()
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.image.name}"


class Word(models.Model):
    name = models.CharField(max_length=100, unique=True)
    count = models.IntegerField(default=0)
    image = models.ManyToManyField(Image, related_name='words')

    def __str__(self):
        return self.name


class UserSettings(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    day_team = models.BooleanField(default=True)
    page_num = models.IntegerField(default=9)
    age = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user.username)
