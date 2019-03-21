from django.shortcuts import render, HttpResponse
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view, action
from rest_framework import viewsets, status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .models import *
from .utility import generate_csv, month_dict
import requests
import json
import pandas as pd
import csv
from django.http import FileResponse
from wsgiref.util import FileWrapper
import os
from .Email import send_mail

# Create your views here.
"""
User Data API
"""


@api_view(["GET"])
def user_list(request, first):
    """
    List all events according to month and year
    """
    if request.method == "GET":
        user = User.objects.filter(username=first)
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)


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
        event = Event.objects.filter(start__month=month, start__year=year)
        serializer = EventSerializer(event, many=True)
        return Response(serializer.data)


# Just use this url and it will downnload the pdf
@api_view(["GET"])
def report_pdf(request, pk):
    if request.method == "GET":
        event = Event.objects.get(id=pk)
        name = event.name
        date = str(event.start)
        date = date[0:10]
        response = HttpResponse(content_type="text/pdf")
        filename = "media/pdf/{}${}.pdf".format(name, date)
        download_name = "{}_Report.pdf".format(name)
        dataset = open(filename, "r")
        response = HttpResponse(dataset, content_type="text/pdf")
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(
            download_name
        )
        return response


# Just use this url and it will downnload the pdf
@api_view(["GET"])
def month_report(request, month):
    """
    List all events according to month and year
    """
    if request.method == "GET":
        event = Event.objects.filter(start__month=month, start__year=2019)
        serializer = EventSerializer(event, many=True)
        r_data = list(serializer.data)
        month_name = month_dict[month]
        filename = "media/csv_month/{}.csv".format(month_name)
        for item in r_data:
            item["start"] = item["start"][0:10]
        start_date = "2019-{}-01".format(month)
        end_date = "2019-{}-31".format(month)
        dates = pd.date_range(start_date, end_date)
        zf = pd.DataFrame(index=dates)
        df = pd.DataFrame.from_dict(r_data)
        df.to_csv(filename)
        nf = pd.read_csv(
            filename, index_col="start", parse_dates=True, na_values=["nan", "NaN"]
        )
        nf = nf.drop(columns=[nf.columns[0], nf.columns[1]])
        zf = zf.join(nf, how="inner")
        zf.to_csv(filename)
        dataset = open(filename, "r")
        response = HttpResponse(dataset, content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="{}_Report.csv"'.format(
            month_name
        )
        return response


@api_view(["GET"])
def event_date(request, date):
    """
    List all Events according to date
    """
    if request.method == "GET":
        event = Event.objects.filter(start__date=date)
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


"""
User Login
"""


# class Login(APIView):
#     serializer_class = LoginSerializer
#
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             user = authenticate(
#                 username=serializer.data.get("username"),
#                 password=serializer.data.get("password"),
#             )
#             login(request, user,backend='django.contrib.auth.backends.ModelBackend')
#             return Response(
#                 serializer.data, status=status.HTTP_201_CREATED
#             )
#         else:
#             return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


"""
User Logout
"""


# class Logout(APIView):
#     def post(self, request):
#         logout(request)
#         # return HttpResponseRedirect(redirect_to="//")


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer


def activate(request, uidb64, token):
    try:
        user = User.objects.get(pk=uidb64)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        # login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        # The login function directly log's in the user without entering credentials
        # Dhairya Here you redirect to Login page and then to calender page ..
        # Http Response added only for testing purpose
        return HttpResponseRedirect('http://localhost:3000/login')

    else:
        # Http Response added only for testing purpose
        return HttpResponse("Failure")


# Model signal on_save -> PDF
# /report/pdf/1 -> Retrieve from MEDIA_URL
# /report/pdf/1/send_email -> Definitely send the Emails
