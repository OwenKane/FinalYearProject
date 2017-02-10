from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Friend
from .models import User


# Create your views here.
@login_required
def view_friends(request):
    current_user = request.user
    friend_id = Friend.objects.filter(user_id=current_user.id, pending=False)
    friend_req_id = Friend.objects.filter(user_id=current_user.id, pending=True)
    users = []
    friend_req = []
    for f in friend_id:
        users.append(User.objects.filter(id=f.friend_id).values('username'))
    for r in friend_req_id:
        friend_req.append(User.objects.filter(id=r.friend_id).values('username'))
    return render(request, 'friends/view_friends.html', {'users': users, 'friend_req': friend_req})
