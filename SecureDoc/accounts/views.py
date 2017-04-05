from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import hashlib


# Create your views here.

# Function to create a new user object
def signup(request):
    if request.method == 'POST':
        # See if confirmation of password was correct
        if request.POST['password1'] == request.POST['password2']:
            # Check to see if the given username is available
            try:
                User.objects.get(username=request.POST['username'])
                return render(request, 'accounts/signup.html', {'error': 'User name has been taken'})
            except User.DoesNotExist:
                # Create new user object with info posted over from the template
                user = User.objects.create_user(request.POST['username'],
                                                password=request.POST['password1'],
                                                email=request.POST['email'],
                                                first_name=request.POST['fname'],
                                                last_name=request.POST['lname'])
                login(request, user)  # Log the new user in
                set_key(request)  # Create the partial key
                print("Signup hash_enc is: " + request.session['hash'])
                return redirect('home')
        else:
            return render(request, 'accounts/signup.html', {'error': 'Passwords didn\'t match'})
    else:
        return render(request, 'accounts/signup.html')


# Create the users partial key
def set_key(request):
    # Split the users password field to get the salt
    user_info = request.user.password.split('$')
    salt = user_info[2]
    # Get the users password that was posted over
    pw = request.POST['password1']
    pw_bytes = pw.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    # Hash the password with the salt to get the partial key
    hash_enc = hashlib.sha256(pw_bytes + salt_bytes).hexdigest()
    # Store locally in the session
    # Server abstracts the sending and receiving of sessions. Session contain a session ID – not the data itself
    # So the server doesnt know what the value is.
    request.session['hash'] = hash_enc
    print("Set key, hash_enc is: " + hash_enc)


# Function to log the user in
def loginview(request):
    if request.method == 'POST':
        # Use Django secure authenticate to verify the user
        user = authenticate(username=request.POST['username'], password=request.POST['password1'])
        if user is not None:
            login(request, user)
            set_key(request)
            # If the user was redirect here from somewhere else, redirect them to the page
            if 'next' in request.POST:
                return redirect(request.POST['next'])
            return redirect('home')
        else:
            return render(request, 'accounts/login.html', {'error': 'Username and password didn\'t match'})
    else:
        return render(request, 'accounts/login.html')


# Logout the view
def logoutview(request):
    if request.method == 'POST':
        # Destroy th session with the partial key
        del request.session['hash']
        logout(request)
        return redirect('home')


def profile(request):
    return render(request, 'accounts/profile.html')

