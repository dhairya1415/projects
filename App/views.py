from django.shortcuts import render
from rest_framework import viewsets
from django.contrib.auth import authenticate, login, logout
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from .serializers import UserSerializer,EventSerializer
from .models import User,Event

# Create your views here.

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
