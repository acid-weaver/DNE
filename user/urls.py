from django.urls import path
from rest_framework.authtoken import views

from user.views import UserViewSet


user_list = UserViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

user_detail = UserViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})


urlpatterns = [
    path('token-auth/', views.obtain_auth_token, name='user-auth'),
    path('', user_list, name='user-list'),
    path('<int:pk>/', user_detail, name='user-detail'),
]
