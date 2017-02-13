from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=200)
    document = models.TextField()
    pub_date = models.DateTimeField()
    author = models.ForeignKey(User, related_name="Author_of_doc")
    edit_options = models.BooleanField(default=False)
    nominated = models.ForeignKey(User, related_name="Nominated_to_view_doc")


    def __str__(self):
        return self.title
