from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Friend
from .models import User


# Create your views here.
@login_required
def view_friends(request):
    users, friend_req = get_friend_info(request)
    return render(request, 'friends/view_friends.html', {'users': users, 'friend_req': friend_req})


def delete_friend(request):
    current_user = request.user
    del_user = request.POST['rm_friend_id']
    Friend.objects.filter(friend_id=del_user).filter(user_id=current_user.id).delete()
    users, friend_req = get_friend_info(request)
    return render(request, 'friends/view_friends.html', {'users': users, 'friend_req': friend_req})


def get_friend_info(request):
    current_user = request.user
    friend_id = Friend.objects.filter(user_id=current_user.id, pending=False)
    friend_req_id = Friend.objects.filter(user_id=current_user.id, pending=True)
    users = []
    friend_req = []
    for f in friend_id:
        users.append(User.objects.filter(id=f.friend_id).values('username', 'id'))
    for r in friend_req_id:
        friend_req.append(User.objects.filter(id=r.friend_id).values('username', 'id'))
    return users, friend_req


def confirm_friend(request):
    current_user = request.user
    req_friend = request.POST['req_friend_id']
    Friend.objects.filter(friend_id=req_friend).filter(user_id=current_user.id).update(pending=False)
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
    id_to_add = User.objects.filter(username=usern).values('id')
    Friend(user_id=current_user.id, friend_id=id_to_add, pending=True)
    users, friend_req = get_friend_info(request)
    return render(request, 'friends/view_friends.html', {'users': users, 'friend_req': friend_req})