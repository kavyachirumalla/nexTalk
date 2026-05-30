# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

def signup_view(request):

    if request.method == "POST":

        username =request.POST.get("username").strip()

        password1 =request.POST.get("password1")

        password2 = request.POST.get("password2")
        if not username or not password1 or not password2:

            return render(
                request,
                "signup.html",
                {
                    "error":
                    "Username and passwords cannot be empty"
                }
            )

        if password1 != password2:

            return render(
                request,
                "signup.html",
                {
                    "error":
                    "Passwords do not match"
                }
            )
        if User.objects.filter(username=username).exists():

            return render(
                request,
                "signup.html",
                {
                    "error":
                    "Username already exists"
                }
            )
        

        user = User.objects.create_user(
            username=username,
            password=password1
        )

        login(request,user)

        return redirect("room_list")

    return render(
        request,
        "signup.html"
    )

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password')
        if not username or not password:
            return render(request, 'login.html', {'error': 'Username and password cannot be empty'})
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('room_list')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')