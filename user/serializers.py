from rest_framework import serializers

from user.models import User
from game.models import Deck


# TODO validation for username, first name, last name!
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'decks', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
        extra_kwargs = {'decks': {'required': False}}

    def validate(self, attrs):
        username = attrs.get('username', None)
        password = attrs.get('password', None)

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("User with this username already exists!")
        if not password or (len(password) < 5):
            raise serializers.ValidationError("Password not provided or its lenght lower than 5!")

        return super().validate(attrs)

    def create(self, validated_data):
        username = validated_data.get('username', None)
        password = validated_data.get('password', None)

        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')

        decks = validated_data.get('decs', [])

        user = User.objects.create_user(username, password, first_name=first_name, last_name=last_name)

        if decks:
            decks = Deck.objects.filter(id__in=decks)
            user.decks.set(decks)

        return user
