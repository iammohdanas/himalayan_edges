from datetime import datetime
import random
import string
from urllib import request
from django.shortcuts import redirect, render
from django.core.mail import send_mail, BadHeaderError
from kashmirguide import settings
from mainapp.filters import TourFilter
from mainapp.forms import BookingForm, ContactForm
from mainapp.models import Agent, Message, Post, Tour
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.utils.text import slugify
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from .models import LoginLogoutActivity
from django.contrib.auth import update_session_auth_hash

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        mobile_no = request.POST['mobile_no']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('register')
        if User.objects.filter(mobile_no=mobile_no).exists():
            messages.error(request, 'Mobile number already registered.')
            return redirect('register')
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False  # Disable account until email is verified
        user.save()

        # Generate email verification token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        verification_link = request.build_absolute_uri(f'/verify-email/{uid}/{token}/')

        # Send verification email
        send_mail(
            'Verify your email',
            f'Click the link to verify your email: {verification_link}',
            'from@example.com',
            [email],
            fail_silently=False,
        )

        messages.success(request, 'Registration successful. Check your email to verify your account.')
        return redirect('login')
    return render(request, 'partial_templates/register.html')

def verify_email_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Email verified successfully. You can now login.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid verification link.')
        return redirect('register')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                LoginLogoutActivity.objects.create(user=user, login_time=timezone.now())
                messages.success(request, 'Login successful.')
                return redirect('home')
            else:
                messages.error(request, 'Account not verified. Check your email.')
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'partial_templates/login.html')

def logout_view(request):
    if request.user.is_authenticated:
        LoginLogoutActivity.objects.filter(user=request.user).latest('login_time').logout_time = timezone.now()
        logout(request)
        messages.success(request, 'Logged out successfully.')
    return redirect('login')

def password_reset_request_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'No user found with the provided email address.')
            return redirect('password_reset_request')

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_link = request.build_absolute_uri(f'/reset-password/{uid}/{token}/')

        # Send password reset email
        send_mail(
            'Password Reset Request',
            f'Click the link to reset your password: {reset_link}',
            'from@example.com',
            [email],
            fail_silently=False,
        )

        messages.success(request, 'Password reset link has been sent to your email.')
        return redirect('login')
    return render(request, 'partial_templates/password_reset_request.html')


def password_reset_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST['password']
            password_confirm = request.POST['password_confirm']

            if password != password_confirm:
                messages.error(request, 'Passwords do not match.')
                return redirect('password_reset', uidb64=uidb64, token=token)

            user.set_password(password)
            user.save()
            update_session_auth_hash(request, user)  # Prevent logout after password change
            messages.success(request, 'Password reset successful. You can now log in with your new password.')
            return redirect('login')

        return render(request, 'partial_templates/password_reset.html')
    else:
        messages.error(request, 'Invalid or expired reset link.')
        return redirect('password_reset_request')


def index(request):
    posts = Post.objects.all().order_by('-publish')[0:4]
    tour = Tour.objects.filter(popular=True, tour_type="featured").order_by('name')[0:8]
    place_id = 'your_place_id_here'  # Replace with the actual Place ID of your location
    # reviews = get_google_reviews(place_id)
    context = {
         'posts': posts,
         'tours': tour,
         'discounted_price' : discounted_price_fun(tour)
        #  'reviews': reviews         
    }
    return render(request, 'index.html', context)

def discounted_price_fun(tour):
    for tour_data in tour:
        if tour_data.discount:
            discounted_price = tour_data.price - (tour_data.price * (tour_data.discount / 100))
        else:
            discounted_price = tour_data.price
    return discounted_price

def handler500(request):
    return render(request, '500.html', status=500)


def tour_list(request):
    tours = Tour.objects.all()  # Fetch all the tours
    context = {
        'tours': tours,
        'discounted_price' : discounted_price_fun(tours)
    }
    print(context)
    return render(request, 'pages/tours.html', context)


def contactView(request):

    form_class = ContactForm
    # if request is not post, initialize an empty form
    form = form_class(request.POST or None)
    if request.method == 'POST':
      
        if form.is_valid():
            name = form.cleaned_data['name']
            subject = form.cleaned_data['subject']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            message = form.cleaned_data['message']
            contact_message = f'Customer  "{name}" with the email {email} just contacted you and left a message  "{message}" please contact him as soon as possible'
            try: 
               send_mail(subject, contact_message, settings.EMAIL_HOST_USER, ['tuksimadventures@gmail.com'], settings.FAIL_SILENTLY)
            except BadHeaderError:
                return HttpResponse('Invalid Header.')
            
            messages.success(request, f"Thank You For Contacting Us { name }, We will Reach You as fast as we can. :)")
            return HttpResponseRedirect(reverse('home'))
            
        else:
            form = ContactForm()
        
    return render(request, 'contact.html', {'form': form})


def tours(request):
    return render(request,"page.html")

def about(request):
    return render(request,"pages/about.html")

def blog(request):
    return render(request,"blog.html")

def adminview(request):
    return render(request, "admin/admin_view.html")

def generate_tour_id():
    date_str = datetime.now().strftime('%y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    tour_id = f"{date_str}{random_str}"
    return tour_id

def tour_list_admin(request):
    tours = Tour.objects.all()
    return render(request, 'admin/tour_list.html', {'tours': tours})

def delete_tour(request):
    if request.method == 'POST':
        tour_id = request.POST.get('tour_id')
        try:
            tour = Tour.objects.filter(tour_id=tour_id)
            tour.delete()
            return JsonResponse({'success': 'Tour deleted successfully'}, status=200)
        except Exception as e:
            messages.error(request,f"Problem occured : {e}")
            return JsonResponse({'error': 'Invalid request method'}, status=405)


def create_tour(request):
    try:
        if request.method == "POST":
            name = request.POST.get('name')
            location = request.POST.get('location')
            tour_type = request.POST.get('tour_type')
            agent_id = request.POST.get('agent_name')  # Retrieve the agent ID
            tour_descr = request.POST.get('tour_descr')
            popular = request.POST.get('popular')
            rating = request.POST.get('rating')
            price = request.POST.get('price')
            discount = request.POST.get('discount')
            summary = request.POST.get('summary')
            daysnights = request.POST.get('daysnights')

            image = request.FILES.get('image')
            image1 = request.FILES.get('image1')
            image2 = request.FILES.get('image2')
            image3 = request.FILES.get('image3')
            image4 = request.FILES.get('image4')

            popular = True if popular == 'on' else False

            tour_id = generate_tour_id()

            fs = FileSystemStorage(location='mainapp/static/images/tours_img')
            image_name = fs.save(f"{tour_id}_{image.name}", image) if image else None
            image1_name = fs.save(f"{tour_id}_{image1.name}", image1) if image1 else None
            image2_name = fs.save(f"{tour_id}_{image2.name}", image2) if image2 else None
            image3_name = fs.save(f"{tour_id}_{image3.name}", image3) if image3 else None
            image4_name = fs.save(f"{tour_id}_{image4.name}", image4) if image4 else None

            # Check if the selected agent exists
            agent = Agent.objects.get(id=agent_id)

            featured_tours = Tour.objects.filter(popular=True, tour_type="featured").count()
            if tour_type == "featured" and featured_tours >= 4:
                raise ValueError("Cannot add more than 4 featured tours.")

            tour = Tour(
                tour_id=tour_id,
                name=name,
                location=location,
                tour_type=tour_type,
                agent_name=agent,  # Assign the agent
                tour_descr=tour_descr,
                summary=summary,
                popular=popular,
                rating=rating,
                tourdays=daysnights,
                price=price,
                discount=discount,
                slug=slugify(name),
                image=image_name,
                image1=image1_name,
                image2=image2_name,
                image3=image3_name,
                image4=image4_name,
            )
            
            # Save the tour
            tour.save()

            messages.success(request, 'Your Tour has been created successfully!')
            return redirect('create_tour')

    except Exception as e:
        messages.error(request, f'There was an error creating the Tour. {e}')

    agents = Agent.objects.all()
    return render(request, 'admin/create_tour_admin.html', {'agents': agents})

from django.shortcuts import render, get_object_or_404

def tour_detail(request, tour_id):
    tour = get_object_or_404(Tour, tour_id=tour_id)
    tour_category = tour.tour_type
    tours = Tour.objects.filter(tour_type = tour_category)
    return render(request, 'pages/tour_detail.html', {'tour': tour, 'tours': tours,'discounted_price' : discounted_price_fun(tours)})

def send_message(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')

        Message.objects.create(
            fullname=fullname,
            email=email,
            phone=phone,
            subject=subject,
            message=message_text
        )

        return redirect('message_list')

    return render(request, 'admin/send_message.html')

def message_list(request):
    messages = Message.objects.filter(seen = False).all().order_by('-timestamp')
    print(messages)
    return render(request, 'admin/message_list.html', {'messages': messages})

def mark_as_seen(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    message.seen = True
    message.save()
    return redirect('message_list')

# def get_google_reviews(place_id):
#     """
#     Fetches Google reviews for a specific place using its Place ID.
#     """
#     google_places_url = (
#         f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={settings.GOOGLE_API_KEY}"
#     )
#     response = request.get(google_places_url)
#     if response.status_code == 200:
#         place_details = response.json()
#         if 'result' in place_details and 'reviews' in place_details['result']:
#             return place_details['result']['reviews']
#     return None


def payment_page(request):
    tour_id = request.POST.get('tour_id')
    tours = Tour.objects.filter(tour_id=tour_id)
    return render(request,"payment/payment_page.html",{'tours': tours})


from django.shortcuts import render, redirect
from .models import Agent
from django.views.decorators.csrf import csrf_exempt

def create_agent_view(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        Agent.objects.create(name=name, email=email, phone_number=phone_number)
        return redirect('list_agents')
    return render(request, 'admin/create_agent.html')

def list_agents_view(request):
    agents = Agent.objects.all()
    return render(request, 'admin/list_agents.html', {'agents': agents})

@csrf_exempt
def delete_agent_view(request, agent_id):
    if request.method == 'POST':
        try:
            agent = Agent.objects.get(id=agent_id)
            agent.delete()
        except Agent.DoesNotExist:
            pass
        return redirect('list_agents')