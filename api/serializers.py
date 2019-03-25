from rest_framework import serializers
from .models import User, Event, Report, Image, Department, Dates
from django.template.loader import render_to_string
from .token import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
import datetime

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

    # def validate(self,data):
    #     start = str(data['start'])[0:10].split('-')
    #     end = str(data['end'])[0:10].split('-')
    #     events = Event.objects.filter(venue = data['event'].venue)
    #     for event in events:
    #         print(event)
    #         dates = Dates.objects.filter(event=event,start__gte = datetime.date(int(start[0]),int(start[1]),int(start[2])),start__lte = datetime.date(int(end[0]),int(end[1]),int(end[2])))
    #         dates_1 = Dates.objects.filter(event=event,end__gte = datetime.date(int(start[0]),int(start[1]),int(start[2])),end__lte = datetime.date(int(end[0]),int(end[1]),int(end[2])))
    #         print(dates)
    #         if (dates or dates_1):
    #             raise serializers.ValidationError('Albatroz')
    #         else:
    #             continue
    #     return data




# End of the month events like continuing to next month Logic -- pending
    def validate(self, data):
        print(data)
        start = str(data['start'])[0:10]
        end = str(data['end'])[0:10]
        start_month = start[0:8]
        end_month = end[0:8]
        start_day = start[8:10]
        end_day = end[8:10]
        events = Event.objects.filter(venue = data['event'].venue)

        print(events)
        for event in events:
            print(event)
            dates = Dates.objects.filter(event=event)
            for date in dates:
                print('Meow --1')
                start_event = str(date.start)[0:10]
                end_event = str(date.end)[0:10]
                start_event_month = start_event[0:8]
                end_event_month = end_event[0:8]
                start_event_day = start_event[8:10]
                end_event_day = end_event[8:10]
                if((start_month == start_event_month) or (start_month == end_event_month) or (end_month == start_event_month) or (end_month == end_event_month) ):
                    print('Meow 2')
                    for i in range (int(start_event_day),(int(end_event_day)+1)):
                        print(i)
                        if (int(start_day) == i or int(end_day) == i):
                            print('meow -4' )
                            raise serializers.ValidationError("Dates occupied for another event")
                        else:
                            print('Meow -5')
                            continue
                else:
                    print('Meow - 6')
                    continue
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
