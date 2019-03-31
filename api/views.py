from django.shortcuts import render, HttpResponse
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view, action
from rest_framework import viewsets, status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .models import *
from .render import render_to_file
from .utility import generate_csv, month_dict
import json
import pandas as pd
import csv
from django.http import FileResponse
from wsgiref.util import FileWrapper
import os
from django.core.mail import EmailMessage
from .Email import send_mail
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

# Create your views here.
"""
User Data API
"""

@api_view(["GET"])
def user_profile(request, username):
    """
    List all events according to month and year
    """
    if request.method == "GET":
        user = User.objects.filter(username=username)
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

    @method_decorator(login_required)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Scheduling of events logic will be here
        serializer.validated_data["creator_name"] = str(
            request.user
        )  # to add .user.first_name
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @method_decorator(login_required)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        if serializer.validated_data["creator_name"] == str(
            request.user
        ):  # to add .user.first_name
            self.perform_update(serializer)
            return Response(serializer.data)

        else:
            raise serializers.ValidationError(
                "You cannot edit the report you are not the creator"
            )


"""
Report API DATA
"""


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    @method_decorator(login_required)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        # serializer.validated_data["event"]["creator_name"] == request.user
        if serializer.validated_data["event"].creator_name == str(
            request.user
        ):  # to add .user.first_name
            self.perform_create(serializer)
            return Response(serializer.data)

        else:
            raise serializers.ValidationError(
                "You cannot create the report you are not the creator"
            )

    @method_decorator(login_required)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        print(serializer.validated_data["event"].creator_name)
        print(request.user)
        if serializer.validated_data["event"].creator_name == str(
            request.user
        ):  # to add .user.first_name
            self.perform_update(serializer)
            return Response(serializer.data)

        else:
            raise serializers.ValidationError(
                "You cannot edit the report you are not the creator"
            )


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

        report_id = serializer.data["report"]
        report = Report.objects.get(pk=report_id)
        event = report.event
        serializer_context = {"request": request}
        report_json = ReportSerializer(report, context=serializer_context).data
        event_json = EventSerializer(event).data
        dates_len = len(event_json["dates"])
        filename = event_json['name']+'$'+event_json["dates"][0]["start"][0:10]
        event_json["dates"] = {'start':event_json["dates"][0]['start'][0:10],'end':event_json["dates"][dates_len-1]['end'][0:10]}
        for items in report_json["image"]:
            items["image"] = items["image"][22::]
            print(items["image"])
        print(report_json["image"])

        params ={
        'report_dict':report_json,
        'event_dict':event_json,
        'request': request,

        }

        render_to_file("pdf.html", params, filename)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

# Here as soon as an image is added the json data of the report generated is taken for pdf generation
# All the function for pdf generation will be called in this create method
# Any update or new image addition will also override the previous csv or pdf generated

"""
Department API data
"""
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    @method_decorator(login_required)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        # serializer.validated_data["event"]["creator_name"] == request.user
        if serializer.validated_data["event"].creator_name == str(
            request.user
        ):  # to add .user.first_name
            self.perform_create(serializer)
            return Response(serializer.data)

        else:
            raise serializers.ValidationError(
                "You cannot assign the department you are not the creator"
            )

    @method_decorator(login_required)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        print(serializer.validated_data["event"].creator_name)
        print(request.user)
        if serializer.validated_data["event"].creator_name == str(
            request.user
        ):  # to add .user.first_name
            self.perform_update(serializer)
            return Response(serializer.data)

        else:
            raise serializers.ValidationError(
                "You cannot edit the departments you are not the creator"
            )



class DatesViewSet(viewsets.ModelViewSet):
    queryset = Dates.objects.all()
    serializer_class = DatesSerializer

    @method_decorator(login_required)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        # serializer.validated_data["event"]["creator_name"] == request.user
        if serializer.validated_data["event"].creator_name == str(
            request.user
        ):  # to add .user.first_name
            self.perform_create(serializer)
            return Response(serializer.data)

        else:
            raise serializers.ValidationError(
                "You cannot assign the dates you are not the creator"
            )

    @method_decorator(login_required)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        print(serializer.validated_data["event"].creator_name)
        print(request.user)
        if serializer.validated_data["event"].creator_name == str(
            request.user
        ):  # to add .user.first_name
            self.perform_update(serializer)
            return Response(serializer.data)

        else:
            raise serializers.ValidationError(
                "You cannot edit the dates you are not the creator"
            )


@api_view(["POST"])
def dates_multiple(request):
    list_dates = request.data
    for date in list_dates:
        x = DatesSerializer(data=date)
        if x.is_valid():
            x.save()

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
        # event = Event.objects.filter(dates__start__month = month,dates__start__year = year)
        # serializer = EventSerializer(event,context={'request':request} ,many=True)
        return Response(serializer.data)


"""
Download PDF
"""


@api_view(["GET"])
def report_pdf_download(request, pk):
    if request.method == "GET":
        report = Report.objects.get(id=pk)
        event = report.event
        event_serializer = EventSerializer(event).data
        name = event_serializer['name']
        date = event_serializer['dates'][0]['start'][0:10]
        response = HttpResponse(content_type="text/pdf")
        filename = "media/pdf/{}${}.pdf".format(name, date)
        download_name = "{}_Report.pdf".format(name)
        dataset = open(filename, "r")
        response = HttpResponse(dataset, content_type="text/pdf")
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(
            download_name
        )
        return response


@api_view(["GET"])
def report_pdf_preview(request, pk):
    if request.method == "GET":
        report = Report.objects.get(id=pk)
        event = report.event
        event_serializer = EventSerializer(event).data
        name = event_serializer['name']
        date = event_serializer['dates'][0]['start'][0:10]
        filename = "media/pdf/{}${}.pdf".format(name,date)
        dataset = open(filename, "r")
        response = HttpResponse(dataset, content_type="application/pdf")
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
        event = Event.objects.filter(dates__start__month=month, dates__start__year=year)
        serializer = EventSerializer(event, many=True)
        serializer = list(serializer.data)
        li = []
        for item in serializer:
            print(item['id'])
            if item["id"] in li:
                serializer.remove(item)
            else:
                li.append(item["id"])
                item["dates"]= {"start":item["dates"][0]["start"],"end":item["dates"][len(item["dates"])-1]["end"]}
                dept_list = []
                for dept in item["departments"]:
                    dept = dept["department"]
                    dept_list.append(dept)
                item["departments"] = dept_list
                item["start"]= item["dates"]["start"][0:10]
                item["end"]= item["dates"]["end"][0:10]
                item.pop('dates')
        month_name = month_dict[month]
        filename = "media/csv_month/{}.csv".format(month_name)
        start_date = "2019-{}-01".format(month)
        end_date = "2019-{}-31".format(month)
        dates = pd.date_range(start_date, end_date)
        zf = pd.DataFrame(index=dates)
        df = pd.DataFrame.from_dict(serializer)
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
User Signup
"""


class SignUp(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer


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
