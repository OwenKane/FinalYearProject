from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Friend
from .models import User
from django.db.models import Q


# Create your views here.

@login_required
def view_friends(request):  # Gets the users friends and request and passes it to the template
    users, friend_req = get_friend_info(request)
    return render(request, 'friends/view_friends.html', {'users': users, 'friend_req': friend_req})


# Delete friend relationship object from database
def delete_friend(request):
    current_user = request.user
    del_id = request.POST['rm_friend_id']
    del_user = User.objects.get(id=del_id)
    Friend.objects.filter(friend=del_user).filter(user=current_user).delete()
    Friend.objects.filter(friend=current_user).filter(user=del_user).delete()
    users, friend_req = get_friend_info(request)
    return render(request, 'friends/view_friends.html', {'users': users, 'friend_req': friend_req})


# Get the users friends and the unconfirmed friend requests
def get_friend_info(request):
    users = get_friends(request)
    friend_req = get_requests(request)
    return users, friend_req


# Get friend objects where pending = true i.e. unconfirmed
def get_requests(request):
    current_user = request.user
    friend_req_id = Friend.objects.filter(
        Q(pending=True),
        Q(friend=current_user)
    ).distinct()
    friend_req = []
    for req in friend_req_id:
        # Add the users (friends) username and id to the array
        friend_req.append(User.objects.filter(id=req.user.id).values('username', 'id'))
    return friend_req


# Get friend objects where pending = false i.e. confirmed
def get_friends(request):
    current_user = request.user
    users = []
    friend_id = Friend.objects.filter(
        Q(pending=False),
        Q(user=current_user) | Q(friend=current_user)
    ).distinct()
    for f in friend_id:
        # Add the users (friends) username and id to the array
        if (User.objects.get(id=f.friend.id)).username == current_user.username:
            users.append(User.objects.filter(id=f.user.id).values('username', 'id'))
        else:
            users.append(User.objects.filter(id=f.friend.id).values('username', 'id'))
    return users


# Update the pending field of the friend object to false
def confirm_friend(request):
    current_user = request.user
    sender_id = request.POST['req_friend_id']
    Friend.objects.filter(user=(User.objects.get(id=sender_id))).filter(friend=current_user).update(pending=False)
    users, friend_req = get_friend_info(request)
    return render(request, 'friends/view_friends.html', {'users': users, 'friend_req': friend_req})


# Delete the friend object to deny the database
def deny_friend(request):
    current_user = request.user
    del_user = request.POST['req_friend_id']
    Friend.objects.filter(friend_id=(User.objects.get(id=del_user))).filter(user_id=current_user).delete()
    users, friend_req = get_friend_info(request)
    return render(request, 'friends/view_friends.html', {'users': users, 'friend_req': friend_req})


# Add new friend object to the database with pending = true
def add_friend(request):
    current_user = request.user
    error = None
    usern = request.POST['username']
    # Try catch, to see if the entered username exists
    try:
        friend_to_add = User.objects.get(username=usern)
        f = Friend(user=current_user, friend=friend_to_add, pending=True)
        f.save()
    except User.DoesNotExist:
        error = "User doesn't exist"
    users, friend_req = get_friend_info(request)
    return render(request, 'friends/view_friends.html', {'users': users, 'friend_req': friend_req, 'error': error})