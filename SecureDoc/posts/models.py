from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=200)
    document = models.TextField()
    pub_date = models.DateTimeField()
    author = models.ForeignKey(User, related_name="Author_of_doc")
    edit_options = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class ShareWith(models.Model):
    doc_id = models.IntegerField()
    author = models.CharField(max_length=200)
    nominated_user = models.CharField(max_length=200)
    edit_options = models.BooleanField(default=False)
