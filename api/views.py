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
import json
import pandas as pd
import csv
from django.http import FileResponse
from wsgiref.util import FileWrapper
import os
from django.core.mail import EmailMessage
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


"""
Event data by month
"""


@api_view(["GET"])
def event_list(request, month, year):
    """
    List all events according to month and year
    """
    if request.method == "GET":
        dates = Dates.objects.filter(start__month=month, start__year=year)
        serializer = DatesSerializer(dates, many=True)
        # event = Event.objects.filter(start__month=month, start__year=year)
        # serializer = EventSerializer(event, many=True)
        return Response(serializer.data)


"""
Event data by date
"""


@api_view(["GET"])
def event_date(request, date):
    """
    List all Events according to date
    """
    if request.method == "GET":
        dates = Dates.objects.filter(start__date=date)
        serializer = DatesSerializer(dates, many=True)
        return Response(serializer.data)


"""
Download PDF
"""


@api_view(["GET"])
def report_pdf(request, pk):
    if request.method == "GET":
        report = Report.objects.get(id=pk)
        name = report.event.name
        date = str(report.event.start)
        users = User.objects.all()
        user_email = []
        for user in users:
            user_email.append(user.email)
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


"""
Generate Month Report
"""


@api_view(["GET"])
def month_report(request, month, year):
    """
    List all events according to month and year
    """
    if request.method == "GET":
        event = Event.objects.filter(start__month=month, start__year=year)
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


"""
Email PDF
"""


@api_view(["GET"])
def send_pdf(request, pk):
    if request.method == "GET":
        report = Report.objects.get(id=pk)
        name = report.event.name
        expert_name = report.event.expert_name
        date = str(report.event.start)
        users = User.objects.all()
        user_email = []
        for user in users:
            user_email.append(user.email)
        date = date[0:10]
        response = HttpResponse(content_type="text/pdf")
        filename = "media/pdf/{}${}.pdf".format(name, date)
        # Send mail on click of download button
        mail_subject = "Report of " + name + " created by " + expert_name
        message = "A pdf of the " + name + " report is sent, Please go through it once."
        to_email = user_email
        for i in range(0, len(to_email)):
            to = to_email[i]
            email = EmailMessage(mail_subject, message, to=[to])
            email.attach_file(filename)
            email.send()

        return response


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

        # report_id = serializer.data["report"]
        # report = Report.objects.get(pk=report_id)
        # event = report.event
        # serializer_context = {"request": request}
        # report_json = ReportSerializer(report, context=serializer_context).data
        # event_json = EventSerializer(event).data
        # print(report_json)
        # generate_csv(report_json, event_json)
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
User Logout
"""


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class DatesViewSet(viewsets.ModelViewSet):
    queryset = Dates.objects.all()
    serializer_class = DatesSerializer


# class Logout(APIView):
#     def post(self, request):
#         logout(request)
#         # return HttpResponseRedirect(redirect_to="//")


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer


"""
User Activation
"""


def activate(request, uidb64, token):
    try:
        user = User.objects.get(pk=uidb64)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse("User Verification Successful")

    else:
        return HttpResponse("User verification failed")


# Model signal on_save -> PDF
# /report/pdf/1 -> Retrieve from MEDIA_URL
# /report/pdf/1/send_email -> Definitely send the Emails
