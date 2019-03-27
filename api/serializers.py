from rest_framework import serializers
from rest_framework.serializers import ValidationError
from .models import User, Event, Report, Image, Department, Dates
from django.template.loader import render_to_string
from .token import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from datetime import datetime



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"

class DatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dates
        fields = "__all__"

    def validate(self, data):
        event_check = data['event']
        start = datetime.date(data['start'])
        end = datetime.date(data['end'])
        event = Event.objects.filter(dates__start__date__lte=start,dates__end__date__gte=end,venue=event_check.venue)
        event_1 = Event.objects.filter(dates__start__date__gte=start,dates__end__date__lte=end,venue=event_check.venue)
        if event.exists() or event_1.exists():
            raise serializers.ValidationError("This location and timing is already occupied.")
        return data


class EventSerializer(serializers.ModelSerializer):
    report = serializers.PrimaryKeyRelatedField(read_only=True)
    departments = DepartmentSerializer(read_only=True, many=True)
    dates = DatesSerializer(read_only=True, many=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "name",
            "allDay",
            "venue",
            "departments",
            "venue",
            "expert_name",
            "description",
            "organizer",
            'creator_name',
            "report",
            "dates",
        )

class ImageSerializer(serializers.HyperlinkedModelSerializer):
    report = serializers.PrimaryKeyRelatedField(queryset=Report.objects.all())

    class Meta:
        model = Image
        fields = "__all__"


class ReportSerializer(serializers.HyperlinkedModelSerializer):
    image = ImageSerializer(read_only=True, many=True)
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())
    event_data = EventSerializer(read_only=True, source="event")

    class Meta:
        model = Report
        fields = (
            "id",
            "event",
            "event_data",
            "number_of_participants",
            "after_event_description",
            "image",
            "attendance",
        )

    # def validate(self, data):
    #
    #     event = data['event']
    #     venue = data['venue']
    #     val_event = Event.objects.filter(dates__start = )
    #     if user_qs.exists():
    #         raise ValidationError("This sap_id already registered.")
    #     return data

class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"})

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "username",
            "password",
            "department",
        )
        extra_kwargs = {"password": {"write_only": True}}

    # Email Verification added here itself do not touch it

    def create(self, validated_data):
        if "djsce.ac.in" in validated_data["email"]:
            user = User(
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                email=validated_data["email"] + '@djsce.ac.in', # + 'djsce.ac.in'
                username=validated_data["username"],
                department=validated_data["department"],
            )
            user.set_password(validated_data["password"])
            user.is_active = False
            user.save()
            mail_subject = "Activate your account."
            message = render_to_string(
                "acc_active_email.html",
                {
                    "user": user,
                    "uidb64": user.pk,
                    "token": account_activation_token.make_token(user),
                },
            )
            to_email = user.email
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return user
        else:
            raise serializers.ValidationError("Email Id does not match the domain @djsce.ac.in")



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=10)
    password = serializers.CharField(
        style={"input_type": "password"}
    )  # ,write_only = True)
