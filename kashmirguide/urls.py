"""
URL configuration for kashmirguide project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from mainapp import views
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('tours/', views.tour_list, name='tours'),
    path('contact/', views.contactView, name='contactus'),
    # path('blog/',views.blog,name="blog"),
    path('about/',views.about, name="about"),
    path('admin-view', views.adminview, name="adminview"),
    path('create-tour', views.create_tour, name='create_tour'),
    path('tour-list/', views.tour_list_admin, name='tour_list'),
    path('delete-tour/',views.delete_tour, name='delete_tour'),
    path('tour/<slug:tour_id>/', views.tour_detail, name='tour_detail'),
    path('send-message/', views.send_message, name='send_message'),
    path('messages/', views.message_list, name='message_list'),
    path('messages/<int:message_id>/seen/', views.mark_as_seen, name='mark_as_seen'),
    path('payment-page/', views.payment_page, name='payment_page'),
    path('create-agent/', views.create_agent_view, name='create_agent'),
    path('agents-list/', views.list_agents_view, name='list_agents'),
    path('delete/<int:agent_id>/', views.delete_agent_view, name='delete_agent'),
    path('submit-review/', views.submit_review, name='submit_review'),
    path('our-team/', views.our_team, name='our_team'),
    path('the-gear-room/', views.gear_room, name='gear_room'),
    path('photo-gallery/', views.photo_gallery, name='photo_gallery'),
    path('', include('authenticator.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)