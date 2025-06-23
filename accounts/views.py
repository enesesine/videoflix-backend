# accounts/views.py

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.db import IntegrityError

from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView

User = get_user_model()


# ────────────────────────────────────────────────────────────────
# Registration
# ────────────────────────────────────────────────────────────────
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("email", "password")

    def create(self, validated_data):
        # Wir verwenden die E-Mail als Username
        email = validated_data["email"]
        password = validated_data["password"]
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            is_active=True,  # überspringen der E-Mail-Verifizierung
        )
        return user


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class   = RegisterSerializer
    queryset           = User.objects.all()  # erforderlich für generics.CreateAPIView

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = serializer.save()
        except IntegrityError:
            # Duplicate username/email
            return Response(
                {"email": ["A user with that email already exists."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Token erstellen
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_201_CREATED)


# ────────────────────────────────────────────────────────────────
# Login per E-Mail + Passwort
# ────────────────────────────────────────────────────────────────
class EmailAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label="E-Mail", write_only=True)
    password = serializers.CharField(
        label="Passwort",
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid credentials."]}
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid credentials."]}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": ["Account is not active."]}
            )

        attrs["user"] = user
        return attrs


class LoginView(ObtainAuthToken):
    permission_classes = [AllowAny]
    serializer_class   = EmailAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_200_OK)


# ────────────────────────────────────────────────────────────────
# Forgot Password: schickt eine Reset-Mail
# ────────────────────────────────────────────────────────────────
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    serializer_class   = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email__iexact=email)
            # Token für Passwort-Reset generieren
            token = default_token_generator.make_token(user)
            # URL zum Frontend-Reset-Flow (achte auf Matching deines Routing-Namens)
            reset_path = reverse('accounts:password_reset_confirm', args=[user.pk, token])
            reset_url  = request.build_absolute_uri(reset_path)
            # Mail verschicken
            send_mail(
                subject="Your Videoflix password reset link",
                message=f"Click here to reset your password: {reset_url}",
                from_email="no-reply@videoflix.com",
                recipient_list=[email],
                fail_silently=False,
            )
        except User.DoesNotExist:
            # Für Sicherheitszwecke keine Info verraten,
            # Rückmeldung bleibt gleich
            pass

        return Response(
            {"detail": "If that email is registered, you will receive a reset link."},
            status=status.HTTP_200_OK
        )
