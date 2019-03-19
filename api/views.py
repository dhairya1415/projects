from django.shortcuts import render, HttpResponse
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view, action
from rest_framework import viewsets, status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .models import *
from .utility import generate_csv
from django.template.loader import render_to_string
from .token import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
import requests
import json

from .Email import send_mail
# Create your views here.
"""
User Data API
"""


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


"""
Event Data API
"""


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


@api_view(["GET"])
def event_list(request, month, year):
    """
    List all events according to month and year
    """
    if request.method == "GET":
        event = Event.objects.filter(start_date__month=month, start_date__year=year)
        serializer = EventSerializer(event, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def event_date(request, date):
    """
    List all Events according to date
    """
    if request.method == "GET":
        event = Event.objects.filter(start_date=date)
        serializer = EventSerializer(event, many=True)
        return Response(serializer.data)


"""
Report API DATA
"""


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer


# def report_getter(request, id):
#     report = Reports.get_object_or_404(pk=id)
#     print(report.venue)


"""
Image API DATA
"""


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        report_api = requests.get(serializer.data["report"])
        report_data = report_api.json()
        event_api = requests.get(report_data["event"])
        event_data = event_api.json()
        generate_csv(report_data, event_data)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


# Here as soon as an image is added the json data of the report generated is taken for pdf generation
# All the function for pdf generation will be called in this create method
# Any update or new image addition will also override the previous csv or pdf generated

"""
User Signup
"""


class SignUp(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        current_site = get_current_site(request)
        mail_subject = 'Activate your account.'
        #The problems are here onwards
        user = request.user
        user.is_active = False
        user.save()
        message = render_to_string('acc_active_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uidb64':user.pk,
        'token':account_activation_token.make_token(user),
    })
        to_email = serializer.data.get('email')
        email = EmailMessage(
                mail_subject, message, to=[to_email]
    )
        email.send()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )





"""
User Login
"""


class Login(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.data.get("username"),
                # password=serializer.data.get("password"),
            )
            login(request, user)
            # backend='django.contrib.auth.backends.ModelBackend'
            return HttpResponseRedirect(redirect_to="//")
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


"""
User Logout
"""


class Logout(APIView):
    def post(self, request):
        logout(request)
        return HttpResponseRedirect(redirect_to="//")


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer


def activate(request, uidb64, token):
    try:
        user = User.objects.get(pk=uidb64)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user,backend='django.contrib.auth.backends.ModelBackend')
        return HttpResponse('Sokcess')
    else:
        return HttpResponse('Failure')


# Model signal on_save -> PDF
# /report/pdf/1 -> Retrieve from MEDIA_URL
# /report/pdf/1/send_email -> Definitely send the Emails
