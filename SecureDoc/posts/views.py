from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Post
from .models import User
from .models import Keys
from .models import ShareWith
from friends.models import Friend
from django.db.models import Q


# Create your views here.


@login_required
def create(request):
    if request.method == 'POST':
        if request.POST.get('title', False) and request.POST.get('test', False):
            post = Post()
            post.title = request.POST.get('title', False)
            post.document = request.POST.get('test', False)
            post.pub_date = timezone.datetime.now()
            post.author = request.user
            post.save()
            key = Keys()
            key.post = Post.objects.get(id=post.id)
            key.author = request.user
            key.key = request.POST.get('key', False)
            key.iv = request.POST.get('iv', False)
            key.save()
            return redirect('home')
        else:
            users = get_friends(request)
            return render(request, 'posts/create.html', {'error': 'Error: Need to fill in all fields', 'users': users})
    else:
        users = get_friends(request)
        return render(request, 'posts/create.html', {'users': users})


@login_required
def home(request):
    current_user = request.user
    posts = Post.objects.all().filter(author=current_user).order_by('-pub_date')
    s_posts = []
    try:
        shared_posts = ShareWith.objects.filter(nominated_user=request.user)
    except ShareWith.DoesNotExist:
        shared_posts = None
    for sp in shared_posts:
        s_posts.append(Post.objects.all().filter(id=sp.post.id))
    return render(request, 'posts/home.html', {'posts': posts, 's_posts': s_posts})


def post_detail(request, post_id):
    postdetails = get_object_or_404(Post, pk=post_id)
    users = get_friends(request)
    return render(request, 'posts/post_detail.html', {'post': postdetails, 'users': users})


def share_editing(request):
    post_id = request.POST['post_id_to_share']
    delete_dup(request, post_id)
    share_with = ShareWith()
    share_with.post = Post.objects.get(id=post_id)
    share_with.author = request.user
    share_with.nominated_user = User.objects.get(username=request.POST['friend_username'])  # This can 404?
    share_with.edit_options = True
    share_with.save()
    postdetails = get_object_or_404(Post, pk=post_id)
    users = get_friends(request)
    return render(request, 'posts/post_detail.html', {'post': postdetails, 'users': users})


def share_viewing(request):
    post_id = request.POST['post_id_to_share']
    delete_dup(request, post_id)
    share_with = ShareWith()
    share_with.post = Post.objects.get(id=post_id)
    share_with.author = request.user
    share_with.nominated_user = User.objects.get(username=request.POST['friend_username'])  # This can 404?
    share_with.edit_options = False
    share_with.save()
    postdetails = get_object_or_404(Post, pk=post_id)
    users = get_friends(request)
    return render(request, 'posts/post_detail.html', {'post': postdetails, 'users': users})


def delete_dup(request, post_id):
    if ShareWith.objects.filter(post=(Post.objects.get(id=post_id)), author=request.user).exists():
        ShareWith.objects.filter(post=(Post.objects.get(id=post_id)), author=request.user).delete()


def update(request):
    if request.method == 'POST':
        if request.POST.get('title', False) and request.POST.get('test', False):
            Post.objects.filter(id=request.POST.get('post_id')).update(
                title=request.POST.get('title', False),
                document=request.POST.get('test', False),
            )
            postdetails = get_object_or_404(Post, pk=request.POST.get('post_id'))
            return render(request, 'posts/post_detail.html', {'post': postdetails})
        else:
            postdetails = get_object_or_404(Post, pk=request.POST.get('post_id'))
            return render(request, 'posts/post_detail.html',
                          {'post': postdetails, 'error': 'Error: Need to fill in all fields'})
    else:
        return render(request, 'posts/create.html')


def update_nominated(request):
    if request.method == 'POST':
        if request.POST.get('test', False):
            post_id = request.POST.get('post_id')
            Post.objects.filter(id=post_id).update(
                document=request.POST.get('test', False),
            )
            post = get_object_or_404(Post, pk=post_id)
            edit_ability = ShareWith.objects.filter(post=post, nominated_user=request.user)
            return render(request, 'posts/view.html', {'post': post, 'edit_ability': edit_ability})
        else:
            post_id = request.POST.get('post_id')
            post = get_object_or_404(Post, pk=post_id)
            edit_ability = ShareWith.objects.filter(post=post, nominated_user=request.user)
            return render(request, 'posts/view.html', {'post': post, 'edit_ability': edit_ability,
                                                       'error': 'Error: Need to fill in all fields'})


def view(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    edit_ability = ShareWith.objects.filter(post=post, nominated_user=request.user)
    return render(request, 'posts/view.html', {'post': post, 'edit_ability': edit_ability})


def get_friends(request):
    current_user = request.user
    users = []
    friend_id = Friend.objects.filter(
        Q(pending=False),
        Q(user_id=current_user.id) | Q(friend_id=current_user.id)
    ).distinct()
    for f in friend_id:
        if (User.objects.get(id=f.friend_id)).username == current_user.username:
            users.append(User.objects.filter(id=f.user_id).values('username', 'id'))
        else:
            users.append(User.objects.filter(id=f.friend_id).values('username', 'id'))
    return users
