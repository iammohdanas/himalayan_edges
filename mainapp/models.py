from datetime import datetime, timezone
from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor.fields import RichTextField

tour_list = [
    ('Trekking', "Trekking"),
    ('Safari', "Safari"),
    ('Island', "Island"),
    ('More', "More")
]

class Post(models.Model):
    STATUS_CHOICES = (('Draft', 'draft'), ('Published', 'published'))
    name = models.CharField(max_length=250, null=True)
    slug = models.SlugField(max_length=250, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = RichTextField(blank=True, null=True)
    image = models.FileField(null=True)
    publish = models.DateTimeField(default=datetime.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    
    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": self.slug})
    

    class Meta:
        ordering = ['-publish']
    
    def __str__(self):
        return self.name

from django.utils.text import slugify

# class Tour(models.Model):
#     TOUR_CHOICES = [
#         ('adventure', 'Adventure'),
#         ('cultural', 'Cultural'),
#         ('beach', 'Beach'),
#         ('featured', 'Featured')
#         # Add more choices as needed
#     ]
#     tour_id = models.CharField(max_length=12, null=True)
#     image = models.ImageField(upload_to='media')
#     name = models.CharField(max_length=100)
#     location = models.CharField(max_length=100)
#     tour_type = models.CharField(choices=TOUR_CHOICES, max_length=20)
#     slug = models.SlugField(max_length=250, blank=True, null=True)
#     tour_descr = models.TextField(blank=True, null=True) 
#     popular = models.BooleanField(blank=True, null=True)
#     rating = models.CharField(max_length=5 ,null=True)

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.name)
#         super(Tour, self).save(*args, **kwargs)

#     def __str__(self):
#         return self.name

class Agent(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    def __str__(self):
        return self.name

class Tour(models.Model):
    TOUR_CHOICES = [
        ('adventure', 'Adventure'),
        ('cultural', 'Cultural'),
        ('beach', 'Beach'),
        ('featured', 'Featured')
    ]
    
    tour_id = models.CharField(max_length=12, null=True)
    image = models.TextField(null=True, blank=True)  # Store Base64 string
    image1 = models.TextField(null=True, blank=True)  # Store Base64 string
    image2 = models.TextField(null=True, blank=True)  # Store Base64 string
    image3 = models.TextField(null=True, blank=True)  # Store Base64 string
    image4 = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=100)
    agent_name = models.CharField(max_length=100,null=True)
    video_link = models.CharField(max_length=200, null=True)
    location = models.CharField(max_length=100)
    tour_type = models.CharField(choices=TOUR_CHOICES, max_length=20)
    slug = models.SlugField(max_length=250, blank=True, null=True)
    tour_descr = RichTextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    popular = models.BooleanField(blank=True, null=True)
    rating = models.CharField(max_length=5, null=True)
    tourdays = models.CharField(max_length=20,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    agent_name = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Tour, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Bookings(models.Model):
    email = models.EmailField()
    full_name = models.CharField(max_length=255, null=True)
    tour_name = models.CharField(max_length=255, null=True)
    quantity = models.PositiveIntegerField()
    message = models.TextField(blank=True, null=True)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return self.full_name

class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    subject = models.CharField(max_length=80)
    message = models.CharField(max_length=20000)

    def __str__(self):
        return self.name


class Message(models.Model):
    fullname = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(default=datetime.now)
    seen = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.fullname} - {self.subject}"
    

class Review(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    country = models.CharField(max_length=100)
    review_text = models.TextField()
    rating = models.IntegerField()  # Assuming rating will be a number (1-5)
    created_at = models.DateTimeField(auto_now_add=True)
    login_email = models.CharField(max_length=100, null=True)
    def __str__(self):
        return f"{self.name} - {self.rating} stars"
    

class Orders(models.Model):
    order_id= models.AutoField(primary_key=True)
    items_json= models.CharField(max_length=5000)
    amount=models.IntegerField(default=0)
    name=models.CharField(max_length=90)
    email=models.CharField(max_length=111)
    address=models.CharField(max_length=111)
    city=models.CharField(max_length=111)
    state=models.CharField(max_length=111)
    zip_code=models.CharField(max_length=111)
    phone=models.CharField(max_length=111, default="")