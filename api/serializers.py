from rest_framework import serializers
from .models import User, Event, Report, Image
from django.template.loader import render_to_string
from .token import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            "id",
            "name",
            "start",
            "end",
            "allDay",
            "department",
            "expert_name",
            "description",
            "organizer",
        )


class ImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"


class ReportSerializer(serializers.HyperlinkedModelSerializer):
    image = serializers.HyperlinkedRelatedField(
        many=True, view_name="image-detail", read_only=True
    )

    class Meta:
        model = Report
        fields = (
            "id",
            "event",
            "venue",
            "number_of_participation",
            "image",
            "attendance",
        )


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
        user = User(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
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


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=10)
    password = serializers.CharField(
        style={"input_type": "password"}
    )  # ,write_only = True)
