"""
accounts.views
Handles registration, login and password-reset endpoints.
"""

# Django —————————————————————————————————————————————————————————————————
from django.contrib.auth import get_user_model                        # project’s custom User model
from django.contrib.auth.tokens import default_token_generator        # built-in token for pw-reset
from django.core.mail import send_mail                                # simple SMTP helper
from django.db import IntegrityError                                  # raised on duplicate e-mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  # UID obfuscation helpers
from django.utils.encoding import force_bytes, force_str              # byte/str conversions
from django.conf import settings                                      # access to FRONTEND_URL, etc.

# DRF ———————————————————————————————————————————————————————————————————
from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny                       # all endpoints are public
from rest_framework.authtoken.models import Token                     # token-auth table
from rest_framework.authtoken.views import ObtainAuthToken            # generic login view
from rest_framework.views import APIView                              # for custom endpoints

User = get_user_model()  # keep a short alias for readability

# ── Registration ────────────────────────────────────────────────────────────
class RegisterSerializer(serializers.ModelSerializer):
    """
    Accepts `email` + `password`, delegates actual user creation to
    `User.objects.create_user()` which handles hashing & validation.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("email", "password")

    # DRF calls `create()` after `.is_valid()`
    def create(self, validated_data):
        # e-mail is reused as username -> single unique field in DB
        return User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            is_active=True,          # skip e-mail verification in this demo
        )


class RegisterView(generics.CreateAPIView):
    """
    `/signup/` – if user is created successfully, immediately issue a
    token so the SPA can store it and redirect to dashboard.
    """

    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    # override to catch duplicate-e-mail race condition cleanly
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
        except IntegrityError:  # unique constraint on e-mail
            return Response(
                {"email": ["A user with that email already exists."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_201_CREATED)

# ── Login ────────────────────────────────────────────────────────────────────
class EmailAuthTokenSerializer(serializers.Serializer):
    """
    Custom auth serializer:
    1. fetch user by e-mail (case-insensitive)
    2. verify password & active flag
    """

    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )

    def validate(self, attrs):
        # 1 — look-up (don’t leak if not found)
        try:
            user = User.objects.get(email__iexact=attrs["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"non_field_errors": ["Invalid credentials."]})

        # 2 — password & active checks
        if not user.check_password(attrs["password"]):
            raise serializers.ValidationError({"non_field_errors": ["Invalid credentials."]})
        if not user.is_active:
            raise serializers.ValidationError({"non_field_errors": ["Account is not active."]})

        attrs["user"] = user  # pass downstream
        return attrs


class LoginView(ObtainAuthToken):
    """Returns `{"token": "<key>"}` on success."""

    permission_classes = [AllowAny]
    serializer_class = EmailAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_200_OK)

# ── Forgot-password mail ─────────────────────────────────────────────────────
class ForgotPasswordSerializer(serializers.Serializer):
    """Single field – we purposely don’t indicate if e-mail exists."""
    email = serializers.EmailField()


class ForgotPasswordView(APIView):
    """
    Always returns 200: prevents user-enumeration by timing / status code.
    Sends Django’s standard password-reset token inside a link to the SPA.
    """

    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email__iexact=email)
            # build tokenised URL for front-end
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{uidb64}/{token}"

            # send simple plaintext mail
            send_mail(
                subject="Your Videoflix password reset link",
                message=f"Click here to reset your password: {reset_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except User.DoesNotExist:
            pass  # silence: same response either way

        return Response(
            {"detail": "If that email is registered, you will receive a reset link."},
            status=status.HTTP_200_OK,
        )

# ── Reset password confirmation ─────────────────────────────────────────────
class ResetPasswordSerializer(serializers.Serializer):
    """
    Verifies `uid` + `token` and sets a new password.
    """

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        # decode user ID
        try:
            uid = force_str(urlsafe_base64_decode(attrs["uid"]))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uid": ["Invalid UID."]})

        # validate token
        if not default_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError({"token": ["Invalid or expired token."]})

        attrs["user"] = user
        return attrs

    def save(self):
        """Persist the new password."""
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class ResetPasswordView(APIView):
    """Final endpoint – simply delegates to the serializer."""

    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )
