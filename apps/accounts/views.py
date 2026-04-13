from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterForm
from django.contrib import messages

from django.contrib.auth import get_user_model
User = get_user_model()

def register_view(request):
    role = request.GET.get('role')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        full_name = request.POST.get('full_name')

        # ✅ Username check
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect(request.path + f"?role={role}")

        # ✅ Password match check
        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect(request.path + f"?role={role}")

        # ✅ Create user manually
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        user.role = role
        user.full_name = full_name
        user.save()

        login(request, user)
        return redirect('dashboard_redirect')

    return render(request, 'accounts/register.html', {'role': role})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard_redirect')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def dashboard_redirect(request):
    user = request.user

    if user.role == 'student':
        return redirect('student_dashboard')
    elif user.role == 'instructor':
        return redirect('instructor_dashboard')
    else:
        return redirect('admin_dashboard')
    
def role_selection(request):
    return render(request, 'home.html')