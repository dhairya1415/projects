from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import *
from .models import User, Event

# Create your views here.

@api_view(['GET',])
def event_list(request, month, year):
    """
    List all code snippets, or create a new
    """
    if request.method == 'GET':
        event = Event.objects.filter(start_date__month = month, start_date__year = year)
        serializer = EventSerializer(event, many=True)
        return Response(serializer.data)

@api_view(['GET',])
def event_date(request, date):
    """
    List all code Event, or create a new Event
    """
    if request.method == 'GET':
        event = Event.objects.filter(start_date = date)
        serializer = EventSerializer(event, many=True)
        return Response(serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class SignUp(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer


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
            return HttpResponseRedirect(redirect_to="//")
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class Logout(APIView):
    def post(self, request):
        logout(request)
        return HttpResponseRedirect(redirect_to="//")
