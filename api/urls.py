"""Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, include

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register("event_custom", views.EventViewSet)
router.register("report", views.ReportViewSet)
router.register("image", views.ImageViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "event/<int:month>/<int:year>", views.event_list, name="month_request"
    ),  # Month data
    path("user/<str:first>", views.user_list, name="profile"),  # user profile data
    path(
        "event/<str:date>", views.event_date, name="date_request"
    ),  # Event data based on month
    path("admin/", admin.site.urls),
    path("signup/", views.SignUp.as_view(), name="signup"),  # Signup
    # path("login/", views.Login.as_view(), name="login"),
    #path("logout/", views.Logout.as_view(), name="logout"),
    path("activate/<str:uidb64>/<str:token>", views.activate, name="activate"),
]

# Dhairya Check these urls
# Login Url:http://127.0.0.1:8000/auth/token/login This will give u a token --
# Logout Url:http://127.0.0.1:8000/auth/token/logout
