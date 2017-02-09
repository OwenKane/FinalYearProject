from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Friend
from .models import User


# Create your views here.
@login_required
def view_friends(request):
    current_user = request.user
    friend_id = Friend.objects.values('friend_id').filter(user_id=current_user.id)
    friends = User.objects.values('username').filter(pk=friend_id)
    print("!!!!!!!!!!!!!!!!!")
    print(friend_id)
    print(friends)
    print("!!!!!!!!!!!!!!!!!")
    return render(request, 'friends/view_friends.html', {'friends': friends})
