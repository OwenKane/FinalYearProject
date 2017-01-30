from django.db import models


# Create your models here.


class List(models.Model):
    title = models.CharField(max_length=250)
    body = models.TextField(default='SOME STRING')

    def __str__(self):
        return self.title
