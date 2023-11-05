from django.contrib import admin
from django.urls import path,include
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.views import MyTokenObtainPairView,Users

class MyTokenRefreshView(TokenRefreshView):
    permission_classes=[AllowAny]

urlpatterns = [
    # users
    path('',Users.as_view()),
    path('admin/', admin.site.urls),
    path('refresh/',MyTokenRefreshView.as_view()),
    path('login/',MyTokenObtainPairView.as_view()),
    # api
    path('api/',include('apps.api.urls'))
]
