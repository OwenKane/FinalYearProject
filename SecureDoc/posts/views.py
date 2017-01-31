from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from . import models


# Create your views here.


@login_required
def create(request):
    if request.method == 'POST':
        if request.POST['title'] and request.POST['document']:
            post = models.Post()
            post.title = request.POST['title']
            post.document = request.POST['document']
            post.pub_date = timezone.datetime.now()
            post.author = request.user
            post.save()
        else:
            return render(request, 'posts/create.html', {'error': 'Error: Need to fill in all fields'})
    else:
        return render(request, 'posts/create.html')
