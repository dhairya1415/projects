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
router.register("event", views.EventViewSet)
router.register("report", views.ReportViewSet)
router.register("image", views.ImageViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("month/<int:month>/<int:year>", views.month_report, name="month_report"),
    path("report_pdf/<int:pk>", views.report_pdf, name="report_pdf"),
    path("send_pdf/<int:pk>",views.send_pdf, name = "send_pdf"),
    path("event/<str:date>", views.event_date, name="date_request"),
    path("event/<int:month>/<int:year>", views.event_list, name="month_request"),
    path("admin/", admin.site.urls),
    path("signup/", views.SignUp.as_view(), name="signup"),  # Signup
    path("activate/<str:uidb64>/<str:token>", views.activate, name="activate"),
]

# Dhairya Check these urls
# Login Url:http://127.0.0.1:8000/auth/token/login This will give u a token --
# Logout Url:http://127.0.0.1:8000/auth/token/logout
