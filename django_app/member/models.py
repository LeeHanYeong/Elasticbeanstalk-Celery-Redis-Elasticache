from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    img_profile = models.ImageField(upload_to='user', blank=True)


class MailResult(models.Model):
    subject = models.CharField(max_length=300)
    message = models.TextField(blank=True)
    recipient_list = models.ManyToManyField(settings.AUTH_USER_MODEL)
    send_at = models.DateTimeField(auto_now_add=True)
    complete_at = models.DateTimeField(blank=True, null=True)

