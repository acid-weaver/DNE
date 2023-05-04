from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from utils.utils import ModelRequestValidator

from game.models import Game, Card, Deck, Player, CardState
from user.models import User
from user.serializers import UserSerializer


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ('id', 'name', 'description', 'type', 'bonus', 'buy_price',
                  'rent_price', 'sp_per_usage', 'created_at', 'updated_at')
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
        fields = ('id', 'game', 'card', 'player', 'owner', 'state',
                  'state_description', 'buy_price', 'rent_price')

    def validate(self, attrs):
        print("cardState serializer")
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
    cards = serializers.ListField(write_only=True)
    users = serializers.ListField(write_only=True)
    # card_states = serializers.ListField()
    # players = serializers.ListField()

    class Meta:
        model = Game
        fields = ('id', 'turn', 'turn_stage', 'card_states', 'players', 'created_at',
                  'updated_at', 'cards', 'users')
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, attrs):
        cards = attrs.get('cards', [])
        card_states = attrs.get('card_states', [])
        users = attrs.get('users', [])
        players = attrs.get('players', [])

        # card_states validation
        if not cards and not card_states:
            raise ValidationError("You are trying to create game without cards!")

        parsed_cards = []
        for card in cards:
            parser = ModelRequestValidator(card, Card)
            card = parser()

            if not card:
                parser.errors()

            parsed_cards.append(card)
            
        # players validation
        if not users and not players:
            raise ValidationError("You are trying to create game without players!")

        parsed_users = []
        for user in users:
            parser = ModelRequestValidator(user, User)
            user = parser()

            if not user:
                parser.errors()

            parsed_users.append(user)

        attrs['cards'] = parsed_cards
        attrs['users'] = parsed_users

        return attrs
    
    def update(self, instance, validated_data):
        print("update")
        # cards = validated_data.get('cards', [])
        # for card in cards:
        #     card_state = CardState.objects.filter(game=instance, card_id=card.id)
        return super().update(instance, validated_data)

    def create(self, validated_data):
        turn = validated_data.get('turn', 0)
        turn_stage = validated_data.get('turn_stage', 0)

        game = Game.objects.create(turn=turn, turn_stage=turn_stage)

        cards = validated_data.get('cards', [])
        for card in cards:
            CardState.objects.create(card=card, game=game,
                                     buy_price=card.buy_price, rent_price=card.rent_price)

        users = validated_data.get('users', [])
        for user in users:
            Player.objects.create(user_id=user.id, game=game)

        return game


class GameSerializer(serializers.ModelSerializer):
    card_states = CardStateSerializer(many=True, validators=[])
    players = PlayerSerializer(many=True, validators=[])

    class Meta:
        model = Game
        fields = ('id', 'turn', 'turn_stage', 'card_states', 'players',
                  'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, attrs):
        print('validation')
        return super().validate(attrs)
    
    def update(self, instance, validated_data):
        print('serializer update')
        return super().update(instance, validated_data)
