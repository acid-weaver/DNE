from rest_framework import serializers

from user.models import User


# TODO validation for username, first name, last name!
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'decks', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
