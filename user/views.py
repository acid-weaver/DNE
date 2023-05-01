from rest_framework.viewsets import ModelViewSet

from user.models import User
from user.serializers import UserSerializer
from utils.permissions import AdminPermission, SelfPermission


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AdminPermission | SelfPermission]

    def list(self, request, *args, **kwargs):
        print(request.user)
        print(request.auth)
        return super().list(request, *args, **kwargs)
