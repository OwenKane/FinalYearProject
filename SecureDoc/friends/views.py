from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Friend
from .models import User
from django.db.models import Q


# Create your views here.
@login_required
def view_friends(request):
    users, friend_req = get_friend_info(request)
    return render(request, 'friends/view_friends.html', {'users': users, 'friend_req': friend_req})


def delete_friend(request):
    current_user = request.user
    del_id = request.POST['rm_friend_id']
    del_user = User.objects.get(id=del_id)
    Friend.objects.filter(friend=del_user).filter(user=current_user).delete()
    Friend.objects.filter(friend=current_user).filter(user=del_user).delete()
    users, friend_req = get_friend_info(request)
    return render(request, 'friends/view_friends.html', {'users': users, 'friend_req': friend_req})


def get_friend_info(request):
    users = get_friends(request)
    friend_req = get_requests(request)
    return users, friend_req


def get_requests(request):
    current_user = request.user
    friend_req_id = Friend.objects.filter(
        Q(pending=True),
        Q(friend=current_user)
    ).distinct()
    friend_req = []
    for req in friend_req_id:
        friend_req.append(User.objects.filter(id=req.user.id).values('username', 'id'))
    return friend_req


def get_friends(request):
    current_user = request.user
    users = []
    friend_id = Friend.objects.filter(
        Q(pending=False),
        Q(user=current_user) | Q(friend=current_user)
    ).distinct()
    for f in friend_id:
        if (User.objects.get(id=f.friend.id)).username == current_user.username:
            users.append(User.objects.filter(id=f.user.id).values('username', 'id'))
        else:
            users.append(User.objects.filter(id=f.friend.id).values('username', 'id'))
    return users


def confirm_friend(request):
    current_user = request.user
    sender_id = request.POST['req_friend_id']
    Friend.objects.filter(user=(User.objects.get(id=sender_id))).filter(friend=current_user).update(pending=False)
    users, friend_req = get_friend_info(request)
    return render(request, 'friends/view_friends.html', {'users': users, 'friend_req': friend_req})


def deny_friend(request):
    current_user = request.user
    del_user = request.POST['req_friend_id']
    Friend.objects.filter(friend_id=(User.objects.get(id=del_user))).filter(user_id=current_user).delete()
    users, friend_req = get_friend_info(request)
    return render(request, 'friends/view_friends.html', {'users': users, 'friend_req': friend_req})


def add_friend(request):
    current_user = request.user
    error = None
    usern = request.POST['username']
    try:
        friend_to_add = User.objects.get(username=usern)
        f = Friend(user=current_user, friend=friend_to_add, pending=True)
        f.save()
    except User.DoesNotExist:
        error = "User doesn't exist"
    users, friend_req = get_friend_info(request)
    return render(request, 'friends/view_friends.html', {'users': users, 'friend_req': friend_req, 'error': error})