from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm, ProfileForm
from .models import LoginOTP
import random
from django.core.mail import send_mail
from django.conf import settings


def register_view(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = ProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            # ❌ Do NOT log in user here
            return redirect('login')  # redirect to login page

    else:
        user_form = UserRegisterForm()
        profile_form = ProfileForm()

    return render(request, 'accounts/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def verify_otp_view(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')

        otp_obj = LoginOTP.objects.filter(
            user=request.user,
            otp=otp_entered,
            is_verified=False
        ).first()

        if otp_obj:
            otp_obj.is_verified = True
            otp_obj.save()
            request.session['otp_verified'] = True

    return redirect('dashboard')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)  # login user session
            request.session['otp_verified'] = False  # OTP not verified

            # Generate OTP
            otp = str(random.randint(100000, 999999))
            LoginOTP.objects.create(user=user, otp=otp)

            # Send OTP to email
            send_mail(
                'Job Portal OTP',
                f'Your OTP is {otp}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False
            )

            return redirect('dashboard')  # dashboard will show OTP overlay

    return render(request, 'accounts/login.html')



def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')


def logout_view(request):
    logout(request)
    return redirect('login')
