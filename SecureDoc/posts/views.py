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

# The @login_ required only allows authenticated users to access the below function
@login_required
def create(request):  # function to create new document
    if request.method == 'POST':
        # Check if the have entered at title and body for the document
        if request.POST.get('title', False) and request.POST.get('doc', False):
            post = Post()
            post.title = request.POST.get('title', False)
            post.document = request.POST.get('doc', False)
            post.pub_date = timezone.datetime.now()
            post.author = request.user
            post.save()  # Save new entry to database
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
    # Display the documents to the user in oder of newest to oldest
    posts = Post.objects.all().filter(author=current_user).order_by('-pub_date')
    s_posts = []
    try:
        shared_posts = ShareWith.objects.filter(nominated_user=request.user)
    except ShareWith.DoesNotExist:
        shared_posts = None
    for sp in shared_posts:
        # append each post object to the array s_post[]
        s_posts.append(Post.objects.all().filter(id=sp.post.id))
    return render(request, 'posts/home.html', {'posts': posts, 's_posts': s_posts})


# For viewing your documents
def post_detail(request, post_id):
    # check if post exists, if it doesnt, display 404 to the user
    postdetails = get_object_or_404(Post, pk=post_id)
    if request.user == postdetails.author:
        users = get_friends(request)
        # Retrieve partial key from db
        cipher = get_object_or_404(Keys, post=postdetails)
        # Server abstracts the sending and receiving of sessions. Session contain a session ID – not the data itself
        # So the server doesnt know what the value is.
        hash_enc = request.session['hash'][-6:]
        shared_with = find_shared(request, post_id)
        return render(request, 'posts/post_detail.html', {'post': postdetails, 'users': users, 'cipher': cipher,
                                                          'hash_enc': hash_enc, 'shared_with': shared_with})
    else:
        return redirect('home')


# To display to the user what documents have been shared with them
def find_shared(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    share_withs = ShareWith.objects.filter(post=post)
    return share_withs


# Allows a user to share their documents with nominated user with editing abilities
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
    # Creating this new entry will allow the selected user to access to the document and edit it
    postdetails = get_object_or_404(Post, pk=post_id)
    key = Keys.objects.get(post=postdetails)
    key.edit_options = True
    key.save()
    # Update the key entry in the table accordingly
    post = Post.objects.get(id=post_id)
    post.document = doc2
    post.save()
    return post_detail(request, post_id)


# Allows a user to share their documents with nominated user with viewing only abilities
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
    # Creating this new entry will allow the selected user to access to the document
    postdetails = get_object_or_404(Post, pk=post_id)
    key = Keys.objects.get(post=postdetails)
    key.edit_options = True
    key.save()
    # Update the key entry in the table accordingly
    post = Post.objects.get(id=post_id)
    post.document = doc
    post.save()
    return post_detail(request, post_id)


# Checks to see if the request will cause a duplicate entry in the db, if it does, delete the entry
def delete_dup(request, post_id):
    if ShareWith.objects.filter(post=(Post.objects.get(id=post_id)), author=request.user).exists():
        ShareWith.objects.filter(post=(Post.objects.get(id=post_id)), author=request.user).delete()


# Sync the document with the database
def update(request):
    if request.method == 'POST':
        # Check if its a post of get request. Adds security
        if request.POST.get('title', False) and request.POST.get('test', False):
            # Update post object with new information
            Post.objects.filter(id=request.POST.get('post_id')).update(
                title=request.POST.get('title', False),
                document=request.POST.get('test', False),
            )
            # Get the updated data and return it back to the user
            postdetails = get_object_or_404(Post, pk=request.POST.get('post_id'))
            return post_detail(request, postdetails.id)
        else:
            postdetails = get_object_or_404(Post, pk=request.POST.get('post_id'))
            return post_detail(request, postdetails.id)
    else:
        return render(request, 'posts/create.html')


# Function to display a document that has been shared with the user
def view(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    edit_ability = ShareWith.objects.filter(post=post, nominated_user=request.user)
    cipher = get_object_or_404(Keys, post=post)
    # hash_enc = request.session['hash'][-6:]
    hash_enc = 1  # DELETE BEFORE SUBMISSION
    return render(request, 'posts/view.html', {'post': post, 'edit_ability': edit_ability, 'cipher': cipher,
                                               'hash_enc': hash_enc})


# Function to populate the friends table when choose to share document with and in the friends section
def get_friends(request):
    current_user = request.user
    users = []
    friend_id = Friend.objects.filter(
        Q(pending=False),
        Q(user_id=current_user.id) | Q(friend_id=current_user.id)
    ).distinct()
    for f in friend_id:
        # For each friend object, get their user name and ad it to the users array
        if (User.objects.get(id=f.friend_id)).username == current_user.username:
            users.append(User.objects.filter(id=f.user_id).values('username', 'id'))
        else:
            users.append(User.objects.filter(id=f.friend_id).values('username', 'id'))
    return users


# Revoke the selected users privileges to the current doc
def revoke(request):
    post_id = request.POST.get('post_id', False)
    username = request.POST.get('username', False)
    post = get_object_or_404(Post, pk=post_id)
    user = User.objects.filter(username=username)
    # Revoke access by deleting the entry in the shareWith table
    ShareWith.objects.filter(post=post, nominated_user=user).delete()
    return post_detail(request, post_id)


# Update a document that has been shared with you and you are nominated to edit
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


# Creates the pdf and temp stores it
def generate_pdf(request):
    try:
        client = pdfcrowd.Client("owenkane", "844e293362c445a06d79a5f5bb6f9900")
        # Name the file the title of the post
        post_title = request.POST['post_title']
        # Creates empty target file
        output_file = open(post_title + '.pdf', 'wb')
        html = request.POST.get('doc2pdf', "Failed")
        client.convertHtml(html, output_file)
        output_file.close()
    except pdfcrowd.Error as why:
        print('Failed:', why)


# Serves the pdf to be downloaded
def download_pdf(request):
    generate_pdf(request)
    # Name the file the title of the post
    post_title = request.POST['post_title']
    file_name = post_title + '.pdf'
    # Put the file in wrapper
    file_wrapper = FileWrapper(open(file_name, 'rb'))
    file_mimetype = mimetypes.guess_type(file_name)
    response = HttpResponse(file_wrapper, content_type=file_mimetype)
    # Send the file as a response that prompts a download
    response['X-Sendfile'] = file_name
    response['Content-Length'] = os.stat(file_name).st_size
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    os.remove(file_name)
    # Delete the temp file
    return response


# Serves the pdf to be downloaded
def download_doc(request):
    generate_doc(request)
    post_title = request.POST['post_title']
    file_name = post_title + '.docx'
    # Put the file in wrapper
    file_wrapper = FileWrapper(open(file_name, 'rb'))
    file_mimetype = mimetypes.guess_type(file_name)
    response = HttpResponse(file_wrapper, content_type=file_mimetype)
    # Send the file as a response that prompts a download
    response['X-Sendfile'] = file_name
    response['Content-Length'] = os.stat(file_name).st_size
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    os.remove(file_name)
    # Delete the temp file
    return response


# Creates the doc and temp stores it
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
    process.download(post_title + '.docx')  # download output file


# Removes the posts object from the DB
def delete_doc(request):
    post_id = request.POST['post_id']
    Post.objects.filter(id=post_id).delete()
    return home(request)