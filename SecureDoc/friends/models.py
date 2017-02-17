from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Friend(models.Model):
    user = models.ForeignKey(User, related_name="%(class)s_User_who_sent_req")
    friend = models.ForeignKey(User, related_name="%(class)s_User_who_received_req")
    pending = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)
