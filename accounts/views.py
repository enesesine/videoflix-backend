from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer, CharField, EmailField
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken


class RegisterSerializer(ModelSerializer):
    email    = EmailField(required=True)
    password = CharField(write_only=True, min_length=8)

    class Meta:
        model  = User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        return User.objects.create_user(
            username   = validated_data["username"],
            email      = validated_data["email"],
            password   = validated_data["password"],
            is_active  = True,  # E-Mail-Verifizierung überspringen
        )


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]       # ← öffentlich
    serializer_class  = RegisterSerializer

    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        token, _ = Token.objects.get_or_create(user=self.object)
        return Response({"token": token.key}, status=status.HTTP_201_CREATED)


class LoginView(ObtainAuthToken):
    permission_classes = [AllowAny]       # ← ebenfalls öffentlich
