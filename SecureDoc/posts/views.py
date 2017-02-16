from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Post
from .models import User
from .models import ShareWith
from friends.models import Friend
from django.db.models import Q


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
            post.edit_options = request.POST['edit_option']
            post.save()
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
        shared_posts = ShareWith.objects.filter(nominated_user=current_user.username)
    except ShareWith.DoesNotExist:
        shared_posts = None
    for sp in shared_posts:
        s_posts.append(Post.objects.all().filter(id=sp.doc_id))
    return render(request, 'posts/home.html', {'posts': posts, 's_posts': s_posts})


def post_detail(request, post_id):
    postdetails = get_object_or_404(Post, pk=post_id)
    users = get_friends(request)
    return render(request, 'posts/post_detail.html', {'post': postdetails, 'users': users})


def share_editing(request):
    post_id = request.POST['post_id_to_share']
    delete_dup(request, post_id)
    share_with = ShareWith()
    share_with.doc_id = post_id
    share_with.author = request.POST['post_author']
    share_with.nominated_user = request.POST['friend_username']
    share_with.edit_options = True
    share_with.save()
    postdetails = get_object_or_404(Post, pk=post_id)
    users = get_friends(request)
    return render(request, 'posts/post_detail.html', {'post': postdetails, 'users': users})


def share_viewing(request):
    post_id = request.POST['post_id_to_share']
    delete_dup(request, post_id)
    share_with = ShareWith()
    share_with.doc_id = post_id
    share_with.author = request.POST['post_author']
    share_with.nominated_user = request.POST['friend_username']
    share_with.edit_options = False
    share_with.save()
    postdetails = get_object_or_404(Post, pk=post_id)
    users = get_friends(request)
    return render(request, 'posts/post_detail.html', {'post': postdetails, 'users': users})


def delete_dup(request, post_id):
    if ShareWith.objects.filter(doc_id=post_id, author=request.user.username).exists():
        ShareWith.objects.filter(doc_id=post_id, author=request.user.username).delete()


def update(request):
    if request.method == 'POST':
        if request.POST.get('title', False) and request.POST.get('document', False):
            Post.objects.filter(id=request.POST.get('post_id')).update(
                title=request.POST.get('title', False),
                document=request.POST.get('document', False),
            )
            postdetails = get_object_or_404(Post, pk=request.POST.get('post_id'))
            return render(request, 'posts/post_detail.html', {'post': postdetails})
        else:
            postdetails = get_object_or_404(Post, pk=request.POST.get('post_id'))
            return render(request, 'posts/post_detail.html',
                          {'post': postdetails, 'error': 'Error: Need to fill in all fields'})
    else:
        return render(request, 'posts/create.html')


def view(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    edit_ability = ShareWith.objects.filter(doc_id=post_id, nominated_user=request.user.username)
    print(edit_ability[0].edit_options)
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
