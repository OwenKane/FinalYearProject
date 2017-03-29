from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import hashlib


# Create your views here.


def signup(request):
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            try:
                User.objects.get(username=request.POST['username'])
                return render(request, 'accounts/signup.html', {'error': 'User name has been taken'})
            except User.DoesNotExist:
                user = User.objects.create_user(request.POST['username'],
                                                password=request.POST['password1'],
                                                email=request.POST['email'],
                                                first_name=request.POST['fname'],
                                                last_name=request.POST['lname'])
                login(request, user)
                user_info = request.user.password.split('$')
                salt = user_info[2]
                pw = request.POST['password']
                pw_bytes = pw.encode('utf-8')
                salt_bytes = salt.encode('utf-8')
                hash_enc = hashlib.sha256(pw_bytes + salt_bytes).hexdigest()
                request.session['hash'] = hash_enc
                return redirect('home')
        else:
            return render(request, 'accounts/signup.html', {'error': 'Passwords didn\'t match'})
    else:
        return render(request, 'accounts/signup.html')


def loginview(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            user_info = request.user.password.split('$')
            salt = user_info[2]
            pw = request.POST['password']
            pw_bytes = pw.encode('utf-8')
            salt_bytes = salt.encode('utf-8')
            hash_enc = hashlib.sha256(pw_bytes + salt_bytes).hexdigest()
            request.session['hash'] = hash_enc
            if 'next' in request.POST:
                return redirect(request.POST['next'])
            return redirect('home')
        else:
            return render(request, 'accounts/login.html', {'error': 'Username and password didn\'t match'})
    else:
        return render(request, 'accounts/login.html')


def logoutview(request):
    if request.method == 'POST':
        del request.session['hash']
        logout(request)
        return redirect('home')


def profile(request):
    return render(request, 'accounts/profile.html')

