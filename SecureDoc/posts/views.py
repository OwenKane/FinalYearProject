import mimetypes
import os
import cloudconvert
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Post
from .models import User
from .models import Keys
from .models import ShareWith
from friends.models import Friend
from django.db.models import Q
import pdfcrowd
from django.http import response
from django.utils.encoding import smart_str
from django.http import HttpResponse
from wsgiref.util import FileWrapper


# Create your views here.


@login_required
def create(request):
    if request.method == 'POST':
        if request.POST.get('title', False) and request.POST.get('doc', False):
            post = Post()
            post.title = request.POST.get('title', False)
            post.document = request.POST.get('doc', False)
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
        hash_enc = request.session['hash'][-6:]
        return render(request, 'posts/create.html', {'users': users, 'hash_enc': hash_enc})


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
    if request.user == postdetails.author:
        users = get_friends(request)
        cipher = get_object_or_404(Keys, post=postdetails)
        hash_enc = request.session['hash'][-6:]
        shared_with = find_shared(request, post_id)
        return render(request, 'posts/post_detail.html', {'post': postdetails, 'users': users, 'cipher': cipher,
                                                          'hash_enc': hash_enc, 'shared_with': shared_with})
    else:
        return redirect('home')


def find_shared(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    share_withs = ShareWith.objects.filter(post=post)
    return share_withs


def share_editing(request):
    post_id = request.POST['post_id']
    doc2 = request.POST.get('doc2', False)
    delete_dup(request, post_id)
    share_with = ShareWith()
    share_with.post = Post.objects.get(id=post_id)
    share_with.author = request.user
    share_with.nominated_user = User.objects.get(username=request.POST['friend_username'])  # This can 404?
    share_with.edit_options = True
    share_with.save()
    postdetails = get_object_or_404(Post, pk=post_id)
    key = Keys.objects.get(post=postdetails)
    key.edit_options = True
    key.save()
    post = Post.objects.get(id=post_id)
    post.document = doc2
    post.save()
    return post_detail(request, post_id)


def share_viewing(request):
    post_id = request.POST['post_id']
    doc = request.POST.get('doc', False)
    delete_dup(request, post_id)
    share_with = ShareWith()
    share_with.post = Post.objects.get(id=post_id)
    share_with.author = request.user
    share_with.nominated_user = User.objects.get(username=request.POST['friend_username'])  # This can 404?
    share_with.edit_options = False
    share_with.save()
    postdetails = get_object_or_404(Post, pk=post_id)
    key = Keys.objects.get(post=postdetails)
    key.edit_options = True
    key.save()
    post = Post.objects.get(id=post_id)
    post.document = doc
    post.save()
    return post_detail(request, post_id)


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
            return post_detail(request, postdetails.id)
        else:
            postdetails = get_object_or_404(Post, pk=request.POST.get('post_id'))
            return post_detail(request, postdetails.id)
    else:
        return render(request, 'posts/create.html')


def view(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    edit_ability = ShareWith.objects.filter(post=post, nominated_user=request.user)
    cipher = get_object_or_404(Keys, post=post)
    hash_enc = request.session['hash'][-6:]
    return render(request, 'posts/view.html', {'post': post, 'edit_ability': edit_ability, 'cipher': cipher,
                                               'hash_enc': hash_enc})


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


def revoke(request):
    post_id = request.POST.get('post_id', False)
    username = request.POST.get('username', False)
    post = get_object_or_404(Post, pk=post_id)
    user = User.objects.filter(username=username)
    ShareWith.objects.filter(post=post, nominated_user=user).delete()
    return post_detail(request, post_id)


def update_nominated(request):
    if request.method == 'POST':
        if request.POST.get('test', False):
            post_id = request.POST.get('post_id')
            Post.objects.filter(id=post_id).update(
                document=request.POST.get('test', False),
            )
            post = get_object_or_404(Post, pk=post_id)
            edit_ability = ShareWith.objects.filter(post=post, nominated_user=request.user)
            cipher = get_object_or_404(Keys, post=post)
            hash_enc = request.session['hash'][-6:]
            return render(request, 'posts/view.html', {'post': post, 'edit_ability': edit_ability, 'cipher': cipher,
                                                       'hash_enc': hash_enc})
        else:
            post_id = request.POST.get('post_id')
            post = get_object_or_404(Post, pk=post_id)
            edit_ability = ShareWith.objects.filter(post=post, nominated_user=request.user)
            cipher = get_object_or_404(Keys, post=post)
            hash_enc = request.session['hash'][-6:]
            return render(request, 'posts/view.html', {'post': post, 'edit_ability': edit_ability,
                                                       'error': 'Error: Need to fill in all fields', 'cipher': cipher,
                                                       'hash_enc': hash_enc})


def generate_pdf(request):
    try:
        client = pdfcrowd.Client("owenkane", "844e293362c445a06d79a5f5bb6f9900")
        post_title = request.POST['post_title']
        output_file = open(post_title + '.pdf', 'wb')
        html = request.POST.get('doc2pdf', "Failed")
        client.convertHtml(html, output_file)
        output_file.close()
    except pdfcrowd.Error as why:
        print('Failed:', why)


def download_pdf(request):
    generate_pdf(request)
    post_title = request.POST['post_title']
    file_name = post_title + '.pdf'
    file_wrapper = FileWrapper(open(file_name, 'rb'))
    file_mimetype = mimetypes.guess_type(file_name)
    response = HttpResponse(file_wrapper, content_type=file_mimetype)
    response['X-Sendfile'] = file_name
    response['Content-Length'] = os.stat(file_name).st_size
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    os.remove(file_name)
    return response


def generate_doc(request):
    generate_pdf(request)
    post_title = request.POST['post_title']
    file_name = post_title + '.pdf'
    api = cloudconvert.Api('ce7WHRtsgw-ZXayCkXX1ke-H53dBWlmnyjw9lzWt5JogRbpV31Fd-W4_8TSsfJmA5D9qpv5TfEAp3ipL5Eba_g')
    process = api.convert({
        'inputformat': 'pdf',
        'outputformat': 'docx',
        'input': 'upload',
        'file': open(file_name, 'rb')
    })
    process.wait()  # wait until conversion finished
    os.remove(file_name)
    process.download(post_title + '.docx')  # download output file


def download_doc(request):
    generate_doc(request)
    post_title = request.POST['post_title']
    file_name = post_title + '.docx'
    file_wrapper = FileWrapper(open(file_name, 'rb'))
    file_mimetype = mimetypes.guess_type(file_name)
    response = HttpResponse(file_wrapper, content_type=file_mimetype)
    response['X-Sendfile'] = file_name
    response['Content-Length'] = os.stat(file_name).st_size
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    return response


def delete_doc(request):
    post_id = request.POST['post_id']
    Post.objects.filter(id=post_id).delete()
    return home(request)