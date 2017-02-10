from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Friend(models.Model):
    user_id = models.IntegerField()
    friend_id = models.IntegerField()
    pending = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)
