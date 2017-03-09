from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=200)
    document = models.TextField()
    pub_date = models.DateTimeField()
    author = models.ForeignKey(User, related_name="%(class)s_Author_of_doc")

    def __str__(self):
        return self.title


class ShareWith(models.Model):
    post = models.ForeignKey(Post, related_name="Linked_to_doc")
    author = models.ForeignKey(User, related_name="%(class)s_Author_of_doc")
    nominated_user = models.ForeignKey(User, related_name="Nominated_user")
    edit_options = models.BooleanField(default=False)


class Keys(models.Model):
    post = models.ForeignKey(Post, related_name="%(class)s_to_doc", null=True)
    author = models.ForeignKey(User, related_name="%(class)s_Author_of_doc")
    key = models.TextField()
    iv = models.TextField(null=True)
