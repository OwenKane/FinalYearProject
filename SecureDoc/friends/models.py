from django.db import models


# Create your models here.

class Friend(models.Model):
    user_id = models.IntegerField()
    friend_id = models.IntegerField()

    def __str__(self):
        return self.id
