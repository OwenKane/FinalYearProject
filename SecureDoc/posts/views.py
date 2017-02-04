from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Post


# Create your views here.


@login_required
def create(request):
    if request.method == 'POST':
        if request.POST.get('title', False) and request.POST.get('document', False):
            post = Post()
            post.title = request.POST.get('title', False)
            post.document = request.POST.get('document', False)
            post.pub_date = timezone.datetime.now()
            post.author = request.user
            post.save()
            return redirect('home')
        else:
            return render(request, 'posts/create.html', {'error': 'Error: Need to fill in all fields'})
    else:
        return render(request, 'posts/create.html')


@login_required
def home(request):
    current_user = request.user
    posts = Post.objects.all().filter(author=current_user).order_by('-pub_date')
    return render(request, 'posts/home.html', {'posts': posts})


def post_detail(request, post_id):
    postdetails = get_object_or_404(Post, pk=post_id)
    return render(request, 'posts/post_detail.html', {'post': postdetails})


def update(request):
    if request.method == 'POST':
        if request.POST.get('title', False) and request.POST.get('document', False):
            Post.objects.filter(id=request.POST.get('post_id')).update(
                title=request.POST.get('title', False),
                document=request.POST.get('document', False)
            )
            postdetails = get_object_or_404(Post, pk=request.POST.get('post_id'))
            return render(request, 'posts/post_detail.html', {'post': postdetails})
        else:
            postdetails = get_object_or_404(Post, pk=request.POST.get('post_id'))
            return render(request, 'posts/post_detail.html', {'post': postdetails, 'error': 'Error: Need to fill in all fields'})
    else:
        return render(request, 'posts/create.html')