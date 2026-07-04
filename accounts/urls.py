from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import RegisterView, PasswordResetRequestView, PasswordResetConfirmView, CustomTokenObtainPairView, CurrentUserView, StaffViewSet

# 🌟 Setup the router for the Staff ViewSet
router = DefaultRouter()
# Registering with an empty string '' means it will respond directly to the base URL 
# (e.g., api/users/ if this file is included under 'users/' in your main urls.py)
router.register(r'', StaffViewSet, basename='staff')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    
    # 👈 Update the login path to use your custom view
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('me/', CurrentUserView.as_view(), name='current-user'),
    # 🌟 Add the router URLs at the bottom!
    path('staff/', include(router.urls)),
]