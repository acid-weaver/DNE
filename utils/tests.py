from rest_framework.test import APIClient
from django.test import TestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model


def remove_timestamps_id(instance_dict:dict) -> dict:
    try:
        instance_dict.pop('updated_at')
        instance_dict.pop('created_at')
        instance_dict.pop('id')
    except:
        print("Cannot remove timestamps and ID.")
        print(f"Provided value to operate:\n{instance_dict}")
    return instance_dict


class BaseTestCaseAPI(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.anon_client = APIClient()
        cls.user_client = APIClient()
        cls.admin_client = APIClient()

        User = get_user_model()
        cls.user = User.objects.create_user(username='Common test-user', password='test321test')
        cls.admin = User.objects.create_superuser(username='Admin test-user', password='test123test')

        user_token = Token.objects.create(user=cls.user)
        admin_token = Token.objects.create(user=cls.admin)

        cls.user_client.force_authenticate(user=cls.user, token=user_token)
        cls.admin_client.force_authenticate(user=cls.admin, token=admin_token)
