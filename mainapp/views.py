import base64
from datetime import datetime
import random
import string
from urllib import request
from django.shortcuts import redirect, render
from django.core.mail import send_mail, BadHeaderError
import requests
from authenticator.decorators import admin_required, role_required
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
from django.shortcuts import render, redirect
from .models import Agent, Orders, Review
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail, BadHeaderError
from django.utils.text import slugify
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def index(request):
    posts = Post.objects.all().order_by('-publish')[:4]
    tours = Tour.objects.filter(tour_type="featured").order_by('name')[:3]
    reviews = Review.objects.all().order_by('-created_at')
    google_reviews = get_google_reviews("ChIJnzlcwPOv4TgRwfAk9LPFUXg")

    tours_with_discounts = [
        {
            "tour_id": tour.tour_id,
            "name": tour.name,
            "location": tour.location,
            "tour_type": tour.tour_type,
            "tour_descr": tour.tour_descr,
            "price": tour.price,
            "discount": str(int(tour.discount)),
            "discounted_price": int(tour.price - (tour.price * (tour.discount / 100)) if tour.discount else tour.price),
            "image": tour.image,
            "popular": tour.popular,
            "summary": tour.summary
        }
        for tour in tours
    ]
    context = {
        'posts': posts,
        'tours': tours_with_discounts,
        'reviews': reviews,
        'google_reviews': google_reviews
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
    tours_with_details = [
        {
            "tour_id": tour.tour_id,
            "name": tour.name,
            "location": tour.location,
            "tour_type": tour.tour_type,
            "tour_descr": tour.tour_descr,
            "summary":tour.summary,
            "price": tour.price,
            "discount": tour.discount,
            "discounted_price": int(tour.price - (tour.price * (tour.discount / 100)) if tour.discount else tour.price),
            "image": tour.image,
            "popular": tour.popular,
        }
        for tour in tours
    ]

    context = {
        'tours': tours_with_details,
    }
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

def our_team(request):
    return render(request, "our_team.html")

def about(request):
    return render(request,"pages/about.html")

def blog(request):
    return render(request,"blog.html")

@login_required
@admin_required
def adminview(request):
    return render(request, "admin/admin_view.html")

def generate_tour_id():
    date_str = datetime.now().strftime('%y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    tour_id = f"{date_str}{random_str}"
    return tour_id

@login_required
@admin_required
def tour_list_admin(request):
    tours = Tour.objects.all()
    return render(request, 'admin/tour_list.html', {'tours': tours})

@login_required
@admin_required
@role_required(['admin', 'manager'])
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

@login_required
@role_required(['admin', 'manager'])
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
            videolink = request.POST.get('videolink')
            image = request.FILES.get('image')
            image1 = request.FILES.get('image1')
            image2 = request.FILES.get('image2')
            image3 = request.FILES.get('image3')
            image4 = request.FILES.get('image4')

            popular = True if popular == 'on' else False

            tour_id = generate_tour_id()

            # Convert images to Base64 strings
            def convert_to_base64(file):
                if file:
                    return base64.b64encode(file.read()).decode('utf-8')
                return None

            image_base64 = convert_to_base64(image)
            image1_base64 = convert_to_base64(image1)
            image2_base64 = convert_to_base64(image2)
            image3_base64 = convert_to_base64(image3)
            image4_base64 = convert_to_base64(image4)

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
                video_link=videolink,
                price=price,
                discount=discount,
                slug=slugify(name),
                image=image_base64,
                image1=image1_base64,
                image2=image2_base64,
                image3=image3_base64,
                image4=image4_base64,
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

@login_required
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
#     # pid_himalayan = "ChIJnzlcwPOv4TgRwfAk9LPFUXg"
#     url = f"https://mybusiness.googleapis.com/v4/accounts/{"location_id"}/reviews"
#     params = {"key": "AIzaSyDwUxAYo298fmazR4GsiFmU_Wr_VHpTYCQ"}
    
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json()  # Reviews data
#     else:
#         return {"error": response.text}


def get_google_reviews( place_id):
    api_key = "AIzaSyAqx1vDs0vqabrN9qRLXBBc0DKdRG1GjU8"
    url = f"https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "reviews",
        "key": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        reviews = data.get("result", {}).get("reviews", [])
        return reviews
    else:
        return JsonResponse({"error": "Failed to fetch reviews"}, status=response.status_code)

@login_required
def payment_page(request):
    tour_id = request.POST.get('tour_id')
    tours = Tour.objects.filter(tour_id=tour_id)
    return render(request,"payment/payment_page.html",{'tours': tours})

@login_required
@admin_required
@role_required(['admin', 'manager'])
def create_agent_view(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        Agent.objects.create(name=name, email=email, phone_number=phone_number)
        return redirect('list_agents')
    return render(request, 'admin/create_agent.html')

@login_required
@admin_required
@role_required(['admin', 'manager'])
def list_agents_view(request):
    agents = Agent.objects.all()
    return render(request, 'admin/list_agents.html', {'agents': agents})

@login_required
@admin_required
@role_required(['admin', 'manager'])
@csrf_exempt
def delete_agent_view(request, agent_id):
    if request.method == 'POST':
        try:
            agent = Agent.objects.get(id=agent_id)
            agent.delete()
        except Agent.DoesNotExist:
            pass
        return redirect('list_agents')

@login_required   
def submit_review(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        country = request.POST.get('country')
        review_text = request.POST.get('review_text')
        rating = request.POST.get('rating')
        login_email =request.user.email
        if name and email and country and review_text and rating:
            try:
                rating = int(rating)
                if 1 <= rating <= 5:
                    Review.objects.create(
                        name=name,
                        email=email,
                        country=country,
                        review_text=review_text,
                        rating=rating,
                        login_email = login_email
                    )
                    return redirect('submit_review')
                else:
                    return HttpResponse("Rating must be between 1 and 5.")
            except ValueError:
                return HttpResponse("Invalid rating. Please enter a number between 1 and 5.")
        else:
            return HttpResponse("All fields are required.")
    return redirect('home')

@login_required
def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone, amount=amount)
        order.save()
        id = order.order_id
        return render(request, 'shop/checkout.html')
    return render(request, 'shop/checkout.html')

def gear_room(request):
    return render(request, "pages/the_gear_room.html")

def photo_gallery(request):
    context = {
        'image_range': range(1, 22)
    }
    return render(request, "pages/photo_gallery.html",context)