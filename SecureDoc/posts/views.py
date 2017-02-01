from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Post


# Create your views here.


@login_required
def create(request):
    if request.method == 'POST':
        if request.POST['title'] and request.POST['document']:
            post = Post()
            post.title = request.POST['title']
            post.document = request.POST['document']
            post.pub_date = timezone.datetime.now()
            post.author = request.user
            post.save()
            return redirect('home')
        else:
            return render(request, 'posts/create.html', {'error': 'Error: Need to fill in all fields'})
    else:
        return render(request, 'posts/create.html')


def home(request):
    posts = Post.objects.order_by('pub_date')
    return render(request, 'posts/home.html', {'posts':posts})