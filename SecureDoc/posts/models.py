from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=200)
    document = models.TextField()
    pub_date = models.DateTimeField()
    author = models.ForeignKey(User)
    nominated = models.TextField()
    edit_options = models.BooleanField(default=False)


    def __str__(self):
        return self.title
