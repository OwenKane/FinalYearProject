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
    del_user = request.POST['rm_friend_id']
    if User.objects.get(id=del_user).username == current_user.username:
        Friend.objects.filter(friend_id=del_user).filter(user_id=current_user.id).delete()
    else:
        Friend.objects.filter(friend_id=current_user.id).filter(user_id=del_user).delete()
    users, friend_req = get_friend_info(request)
    print(User.objects.get(id=del_user).username)
    return render(request, 'friends/view_friends.html', {'users': users, 'friend_req': friend_req})


def get_friend_info(request):
    users = get_friends(request)
    friend_req = get_requests(request)
    return users, friend_req


def get_requests(request):
    current_user = request.user
    friend_req_id = Friend.objects.filter(
        Q(pending=True),
        Q(friend_id=current_user.id)
    ).distinct()
    friend_req = []
    for req in friend_req_id:
        friend_req.append(User.objects.filter(id=req.user_id).values('username', 'id'))
    return friend_req


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


def confirm_friend(request):
    current_user = request.user
    sender_id = request.POST['req_friend_id']
    Friend.objects.filter(user_id=sender_id).filter(friend_id=current_user.id).update(pending=False)
    users, friend_req = get_friend_info(request)
    return render(request, 'friends/view_friends.html', {'users': users, 'friend_req': friend_req})


def deny_friend(request):
    current_user = request.user
    del_user = request.POST['req_friend_id']
    Friend.objects.filter(friend_id=del_user).filter(user_id=current_user.id).delete()
    users, friend_req = get_friend_info(request)
    return render(request, 'friends/view_friends.html', {'users': users, 'friend_req': friend_req})


def add_friend(request):
    current_user = request.user
    usern = request.POST['username']
    id_to_add = User.objects.get(username=usern).pk
    print(id_to_add)
    f = Friend(user_id=current_user.id, friend_id=id_to_add, pending=True)
    f.save()
    users, friend_req = get_friend_info(request)
    return render(request, 'friends/view_friends.html', {'users': users, 'friend_req': friend_req})