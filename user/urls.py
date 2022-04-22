from django.urls import path
from .views.userview import CustomAuthToken, UserCreateAPIView, UserAPIView
from rest_framework import routers

app_name = 'user'
router = routers.SimpleRouter()

router.register('create', UserCreateAPIView, 'create-user')
router.register('', UserAPIView, 'user')

urlpatterns = tuple(router.urls)

urlpatterns += (
    path('login', CustomAuthToken.as_view(), name='login'),
)
