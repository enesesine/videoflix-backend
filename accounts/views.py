# accounts/views.py

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.db import IntegrityError
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView

User = get_user_model()


# ─────────────── Register ───────────────
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("email", "password")

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]
        user = User.objects.create_user(
            username=email, email=email, password=password, is_active=True
        )
        return user


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class    = RegisterSerializer
    queryset            = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
        except IntegrityError:
            return Response(
                {"email": [_("A user with that email already exists.")]},
                status=status.HTTP_400_BAD_REQUEST
            )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_201_CREATED)


# ─────────────── Login ───────────────
class EmailAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"non_field_errors": [_("Invalid credentials.")]}
            )
        if not user.check_password(password):
            raise serializers.ValidationError(
                {"non_field_errors": [_("Invalid credentials.")]}
            )
        if not user.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": [_("Account is not active.")]}
            )
        attrs["user"] = user
        return attrs


class LoginView(ObtainAuthToken):
    permission_classes = [AllowAny]
    serializer_class   = EmailAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_200_OK)


# ─────────────── Forgot Password ───────────────
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                _("No user is associated with this email address.")
            )
        return value

    def save(self, request=None):
        """
        Send password reset email using Django's built-in form.
        """
        form = PasswordResetForm(data={"email": self.validated_data["email"]})
        form.is_valid()  # prüft intern nochmal
        # Hier kannst du deine eigenen Templates hinterlegen
        form.save(
            subject_template_name="registration/password_reset_subject.txt",
            email_template_name="registration/password_reset_email.html",
            request=request,
            html_email_template_name=None,
        )


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request=request)
        return Response(
            {"detail": _("If an account with that email exists, you will receive a password reset email shortly.")},
            status=status.HTTP_200_OK
        )
