
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from urllib.parse import quote
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


from .serializers import RegisterSerializer, ActivateSerializer, LoginSerializer, PasswordConfirmSerializer
from core.utils.tasks import enqueue_after_commit
from auth_app.tasks import send_activation_email, send_passwordreset_email

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
           Register View, after reigstration a activation email will be sent to the user
        """
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = f"http://127.0.0.1:5500/pages/auth/activate.html?uid={quote(uidb64)}&token={quote(token)}"

        enqueue_after_commit(send_activation_email, user.email, activation_link)

        return Response({
            "user": {
                "id": user.id,
                "email": user.email
            },
            "token": token
        }, status=status.HTTP_201_CREATED)
    

class ActivateView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, uidb64, token):
        """
            Activate User
        """
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({
                'message': 'Invliad activation link.'
            }, status=status.HTTP_400_BAD_REQUEST)
        

        if default_token_generator.check_token(user, token):
            if not user.is_active:

                serializer = ActivateSerializer(user, data={}, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({
                    'message': 'User is now activated.'
                }, status=status.HTTP_200_OK)
            else: 
                return Response({
                    'message': 'User is already activated.'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'message': 'Invliad activation link.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
        

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        """
           Login View accept post 
        """
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response({'message': 'Email or Password wrong'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.validated_data['user']
        refresh = serializer.validated_data['refresh']
        access = serializer.validated_data['access']

        response = Response({
                "detail": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.email
                }
            }, status=status.HTTP_200_OK)
        
        access_token_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
        refresh_token_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']

        response.set_cookie(
            key='access_token',
            value = str(access),
            httponly=True,
            samesite='Lax',
            max_age=int(access_token_lifetime.total_seconds())
        )

        response.set_cookie(
            key='refresh_token',
            value = str(refresh),
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=int(refresh_token_lifetime.total_seconds())
        )
        
        return response
    

class LogoutView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        """
            Login out and delete all cookies
        """
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token is None:
            return Response({'detail': 'Refresh token not found.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            response = Response({"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."}, status=status.HTTP_200_OK)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')

            return response
        except Exception:
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)
    

class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        """
            Refresh access_token by passing refresh_token to serializer
        """
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token is None:
            return Response({'detail': 'Refresh token not found.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data={'refresh': refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except (ValidationError, TokenError):
            return Response({'detail': 'Refresh token is invalid'}, status=status.HTTP_401_UNAUTHORIZED)
    
        access_token = serializer.validated_data.get('access')
        
        response = Response({
            "detail": "Token refreshed",
            "access": access_token
            })
        
        response.set_cookie(key='access_token', value=access_token, httponly=True, samesite='Lax')
        return response


class PasswordResetView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        """
            Reset Pasword by taking email as paramater
        """
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'email is invalid'}, status=status.HTTP_400_BAD_REQUEST)
        
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f'http://127.0.0.1:5500/pages/auth/confirm_password.html?uid={uidb64}&token={token}'

        enqueue_after_commit(send_passwordreset_email, user.email, reset_link)
      
        return Response({
                'detail': 'An email has been sent to reset your password.'
            }, status=status.HTTP_200_OK)
    
    
class PasswordConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        """
            Activate User by sending uid 
        """
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({
                'detail': 'Invliad activation link.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if default_token_generator.check_token(user, token):
            serializer = PasswordConfirmSerializer(instance=user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                  "detail": "Your Password has been successfully reset."
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'detail': 'Invliad activation link.'
            }, status=status.HTTP_400_BAD_REQUEST)


    

        


