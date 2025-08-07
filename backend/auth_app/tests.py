from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken



User = get_user_model()

class AuthViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            is_active=True
        )

    def test_register_view(self):
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'confirmed_password': "newpass123"

        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)

    def test_activate_view_valid(self):
        user = User.objects.create_user(username='toactivate', email='toactivate@example.com', password='pass', is_active=False)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
       
        token = default_token_generator.make_token(user)
        url = reverse('activate', kwargs={'uidb64': uidb64, 'token': token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_activate_view_invalid(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = 'invalidtoken'
        url = reverse('activate', kwargs={'uidb64': uidb64, 'token': token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_view(self):
        url = reverse('login-in')
        data = {
            'email': self.user.email,
            'password': 'testpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)

    def test_logout_view_valid(self):
        refresh = RefreshToken.for_user(self.user)
        url = reverse('login-out')
        self.client.cookies['refresh_token'] = str(refresh)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_view_no_cookie(self):
        url = reverse('login-out')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_refresh_view_valid(self):
        refresh = RefreshToken.for_user(self.user)
        url = reverse('token-refresh')
        self.client.cookies['refresh_token'] = str(refresh)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('access_token', response.cookies)

    def test_token_refresh_view_invalid(self):
        url = reverse('token-refresh')
        self.client.cookies['refresh_token'] = 'invalidtoken'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_reset_valid_email(self):
        url = reverse('password-reset')
        response = self.client.post(url, {'email': self.user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_invalid_email(self):
        url = reverse('password-reset')
        response = self.client.post(url, {'email': 'invalid@example.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_confirm_valid(self):
        token = default_token_generator.make_token(self.user)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        url = reverse('password-confirm', kwargs={'uidb64': uidb64, 'token': token})
        data = {
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_confirm_invalid_token(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = 'invalid-token'
        url = reverse('password-confirm', kwargs={'uidb64': uidb64, 'token': token})
        data = {
            'new_password1': 'irrelevant',
            'new_password2': 'irrelevant'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

