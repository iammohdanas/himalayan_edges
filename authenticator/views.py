from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.models import User
from dotenv import load_dotenv
from .models import Profile
from django.utils.crypto import get_random_string
import hashlib
import random
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from twilio.rest import Client  # Twilio for SMS
from django.core.mail import send_mail
from django.contrib.auth.models import User
load_dotenv()

# Function to send the verification email
def send_verification_email(user):
    token = hashlib.sha256(str(random.random()).encode('utf-8')).hexdigest()
    user.profile.verification_token = token
    user.profile.save()
    verification_url = f'http://localhost:8000/auth_system/verify-email/{token}/'
    send_mail(
        'Email Verification',
        f'Click the link to verify your email: {verification_url}',
        'your_email@example.com',  # Update with your email
        [user.email],
        fail_silently=False,
    )

# Register user and send email verification
def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        mobile_number = request.POST['mobile_number']
        terms_accepted = request.POST.get('terms_accepted')

        if not terms_accepted:
            messages.error(request, "Please accept the terms and conditions.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        user = User.objects.create_user(
            username=username, email=email, password=password, first_name=first_name, last_name=last_name
        )
        profile = Profile.objects.get(user=user)
        profile.mobile_number = mobile_number
        profile.save()

        send_verification_email(user)
        messages.info(request, "Registration successful! Please verify your email.")
        return redirect('login')

    return render(request, 'auth_template.html')

# Login view with email verification check
def login_view(request):
    # import pdb; pdb.set_trace()
    if request.method == 'POST':
        user_input = request.POST.get('username_or_email', '').strip()
        password_fields = [key for key in request.POST if 'password' in key]
        if password_fields:
            password = request.POST[password_fields[0]]  # Assuming you want the first match

        # Determine if input is email or username
        if '@' in user_input and '.' in user_input:
            # Treat input as email
            user = User.objects.filter(email=user_input).first()
            if user:
                username = user.username  # Retrieve the username for authentication
            else:
                username = None
        else:
            # Treat input as username
            username = user_input

        if username:
            # Authenticate user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if not user.profile.is_email_verified:
                    messages.error(request, "Please verify your email first.")
                    return redirect('login')

                login(request, user)

                if not user.profile.first_login_done:
                    # Send welcome email/message here
                    user.profile.first_login_done = True
                    user.profile.save()

                messages.success(request, "Login successful!")
                return redirect('home')  # Redirect to the main page
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or email.")
    
    return render(request, 'auth_template.html')

# Logout view
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')

# Verify email address
def verify_email(request, token):
    try:
        profile = Profile.objects.get(verification_token=token)
        profile.is_email_verified = True
        profile.verification_token = ''
        profile.save()
        messages.success(request, "Email verified successfully! You can now log in.")
        return redirect('login')
    except Profile.DoesNotExist:
        messages.error(request, "Invalid verification link.")
        return redirect('register')

# OTP verification for password reset
def send_sms_otp(mobile_number, otp):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f'Your password reset OTP is: {otp}',
        from_=TWILIO_PHONE_NUMBER,
        to=mobile_number
    )
    return message.sid

# Forgot password view
def forgot_password(request):
    if request.method == 'POST':
        identifier = request.POST['identifier']  # Can be email or mobile number
        try:
            user = User.objects.get(email=identifier) if '@' in identifier else User.objects.get(profile__mobile_number=identifier)
            otp = user.profile.generate_otp()

            if '@' in identifier:  # Email-based OTP
                send_mail(
                    'Password Reset OTP',
                    f'Your OTP for password reset is: {otp}',
                    EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )
                messages.info(request, "An OTP has been sent to your email.")
            else:  # Mobile-based OTP
                send_sms_otp(user.profile.mobile_number, otp)
                messages.info(request, "An OTP has been sent to your mobile number.")

            return redirect('verify_otp', user_id=user.id)  # Redirect to OTP verification page
        except User.DoesNotExist:
            messages.error(request, "No account found with this identifier.")
            return redirect('forgot_password')

    return render(request, 'auth_template.html')

# OTP verification view
def verify_otp(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        otp = request.POST['otp']
        if user.profile.otp == otp:
            messages.success(request, "OTP verified successfully. Please set a new password.")
            return redirect('reset_password', user_id=user.id)  # Redirect to reset password page
        else:
            messages.error(request, "Invalid OTP.")
    return render(request, 'auth_template.html')

# Reset password view
def reset_password(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        if new_password == confirm_password:
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password reset successful. Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")
    return render(request, 'auth_template.html')

@login_required
def delete_account(request):
    user = request.user
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('register')
    return render(request, 'auth_template.html') 
