from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from game.models import Game, Card, Deck, Player, CardState
from user.models import User
from user.serializers import UserSerializer


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ('id', 'name', 'description', 'type', 'bonus', 'buy_price', 'rent_price', 'sp_per_usage', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class DeckSerialier(serializers.ModelSerializer):
    cards = CardSerializer(many=True)

    class Meta:
        model = Deck
        fields = ('id', 'name', 'cards', 'owner', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class PlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Player
        fields = ('id', 'user', 'game', 'lvl', 'energy', 'bankroll', 'sp')
        read_only_fields = ('user', 'game')


# TODO relize all methods "from hand"
class CardStateSerializer(serializers.ModelSerializer):
    card = CardSerializer()

    class Meta:
        model = CardState
        fields = ('id', 'game', 'card', 'player', 'owner', 'state', 'state_description', 'buy_price', 'rent_price')

    def validate(self, attrs):
        card_id = attrs.get('card', None)

        try:
            card = Card.objects.get(id=card_id)
            attrs['card'] = card
        except:
            raise ValidationError('Card info not provided or invalid card id!')

        return super().validate(attrs)

    def create(self, validated_data):
        owner = validated_data.get('owner', None)
        buy_price = validated_data.get('buy_price', None)
        rent_price = validated_data.get('rent_price', None)
        card = validated_data.get('card', None)

        if (owner is None) and (buy_price is None):
            buy_price = card.buy_price
        if (owner is None) and (rent_price is None):
            rent_price = card.rent_price

        return super().create(validated_data)


class GameCreateSerializer(serializers.ModelSerializer):
    cards = serializers.ListField(required=True, write_only=True)
    users = serializers.ListField(required=True, write_only=True)

    class Meta:
        model = Game
        fields = ('id', 'turn', 'turn_stage', 'card_states', 'players', 'created_at', 'updated_at', 'cards', 'users')
        read_only_fields = ('created_at', 'updated_at', 'card_states', 'players')

    def validate(self, attrs):
        cards = attrs.get('cards', [])
        users = attrs.get('users', [])

        # card_states validation
        if len(cards) == 0:
            raise ValidationError("You are trying to create game without cards!")

        for card in cards:
            if not isinstance(card, int):
                raise ValidationError("Cards must be provided as their ID's (list of int) "
                                      "while you create game")
            try:
                Card.objects.get(id=card)
            except:
                raise ValidationError(f"No card with ID {card}.")
            
        # players validation
        if len(users) == 0:
            raise ValidationError("You are trying to create game without players!")
        
        for user in users:
            if not isinstance(user, int):
                raise ValidationError("Users must be provided as their ID's (list of int) "
                                      "while you create game")
            try:
                User.objects.get(id=user)
            except:
                raise ValidationError(f"No user with ID {user}.")

        return super().validate(attrs)

    def create(self, validated_data):
        turn = validated_data.get('turn', 0)
        turn_stage = validated_data.get('turn_stage', 0)

        game = Game.objects.create(turn=turn, turn_stage=turn_stage)

        card_ids = validated_data.get('cards', [])
        for card_id in card_ids:
            card = Card.objects.get(id=card_id)
            CardState.objects.create(card=card, game=game, buy_price=card.buy_price, rent_price=card.rent_price)

        user_ids = validated_data.get('users', [])
        for user_id in user_ids:
            Player.objects.create(user_id=user_id, game=game)

        return game


class GameSerializer(serializers.ModelSerializer):
    card_states = CardStateSerializer(many=True)
    players = PlayerSerializer(many=True)

    class Meta:
        model = Game
        fields = ('id', 'turn', 'turn_stage', 'card_states', 'players', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
