from django.urls import path
from .views import SuperAdminLoginView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('login-admin/', SuperAdminLoginView.as_view(), name='token_obtain_pair'),
    # path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]