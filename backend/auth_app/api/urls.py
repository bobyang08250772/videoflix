from django.urls import path
from .views import RegisterView, ActivateView, LoginView, CustomTokenRefreshView, LogoutView, PasswordResetView, PasswordConfirmView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivateView.as_view(), name='activate'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('login/', LoginView.as_view(), name='login-in'),
    path('logout/', LogoutView.as_view(), name='login-out'),
    path('password_reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password_confirm/<uidb64>/<token>/', PasswordConfirmView.as_view(), name='password-confirm'),

]
