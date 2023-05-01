from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from game.models import Game, Card, Deck, Player, CardState
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


class GameSerializer(serializers.ModelSerializer):
    card_states = CardStateSerializer(many=True)
    players = PlayerSerializer(many=True)

    class Meta:
        model = Game
        fields = ('id', 'turn', 'turn_stage', 'card_states', 'players', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def create(self, validated_data):
        turn = 0
        turn_stage = 0
        game = Game.objects.create()
        cards = validated_data.get('card_states', [])

        for card in cards:
            card_id = card.get('id', None)

            # TODO relize it in validation
            if not card_id:
                raise ValidationError("You trying create game, but provided card(s) doesn't exist!")

            card_data = {
                'card': card_id,
                'game': game.id,
                'player': None,
                'owner': None,
            }
            card_serializer = CardStateSerializer(data=card_data)
        return game
