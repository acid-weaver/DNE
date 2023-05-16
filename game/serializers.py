from rest_framework.serializers import (ModelSerializer,
                                        ListField)
from rest_framework.exceptions import ValidationError
from utils.utils import NestedModelHandler

from game.models import Game, Card, Deck, Player, CardState
from user.models import User
from user.serializers import UserSerializer


class CardSerializer(ModelSerializer):
    class Meta:
        model = Card
        fields = ('id', 'name', 'description', 'type', 'bonus', 'buy_price',
                  'rent_price', 'sp_per_usage', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class DeckSerialier(ModelSerializer):
    cards = CardSerializer(many=True)

    class Meta:
        model = Deck
        fields = ('id', 'name', 'cards', 'owner', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class PlayerSerializer(ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'user', 'game', 'lvl', 'energy', 'bankroll', 'sp')
        read_only_fields = ('user', 'game')


class PlayerCreateSerializer(ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'user', 'game', 'lvl', 'energy', 'bankroll', 'sp')


# TODO relize all methods "from hand"
class CardStateSerializer(ModelSerializer):
    card = CardSerializer()

    class Meta:
        model = CardState
        fields = ('id', 'game', 'card', 'player', 'owner', 'location',
                  'status', 'buy_price', 'rent_price')


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


class CardStateAdminSerializer(ModelSerializer):
    class Meta:
        model = CardState
        fields = ('id', 'game', 'card', 'player', 'owner', 'location',
                  'status', 'buy_price', 'rent_price')


class GameCreateSerializer(ModelSerializer):
    cards = ListField(write_only=True)
    users = ListField(write_only=True)

    class Meta:
        model = Game
        fields = ('id', 'turn', 'turn_stage', 'cards', 'users',
                  'card_states', 'players', 'created_at', 'updated_at')
        read_only_fields = ('card_states', 'players', 'created_at', 'updated_at')


    def validate(self, attrs):
        cards = attrs.get('cards', [])
        users = attrs.get('users', [])

        # card_states validation
        if not cards:
            raise ValidationError("You are trying to create game without cards!")

        parsed_cards = []
        for card in cards:
            handler = NestedModelHandler(card, Card)
            card = handler.get_instance()

            parsed_cards.append(card)
            
        # players validation
        if not users:
            raise ValidationError("You are trying to create game without players!")

        parsed_users = []
        for user in users:
            handler = NestedModelHandler(user, User)
            user = handler.get_instance()

            parsed_users.append(user)

        attrs['cards'] = parsed_cards
        attrs['users'] = parsed_users

        return attrs

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


class GameUpdateSerializer(ModelSerializer):
    card_states = ListField(write_only=True)
    players = ListField(write_only=True)

    class Meta:
        model = Game
        fields = ('id', 'turn', 'turn_stage', 'card_states', 'players', 'created_at',
                  'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, attrs):
        card_states = attrs.get('card_states', [])
        players = attrs.get('players', [])

        card_handlers = []
        for card_state in card_states:
            handler = NestedModelHandler(card_state, CardState)
            handler.validate(CardStateAdminSerializer, context=self.context)
            card_handlers.append(handler)

        player_handlers = []
        for player in players:
            handler = NestedModelHandler(player, Player)
            handler.validate(PlayerCreateSerializer, context=self.context)
            card_handlers.append(handler)

        attrs['card_handlers'] = card_handlers
        attrs['player_handlers'] = player_handlers

        return attrs

    def update(self, instance, validated_data):
        turn = validated_data.get('turn', None)
        turn_stage = validated_data.get('turn_stage', None)
        card_handlers = validated_data.get('card_handlers', [])
        player_handlers = validated_data.get('player_handlers', [])

        for handler in card_handlers:
            handler.update()

        for handler in player_handlers:
            handler.update()

        if not turn is None:
            instance.turn = turn
        if not turn_stage is None:
            instance.turn_stage = turn_stage

        return instance


class GameSerializer(ModelSerializer):
    card_states = CardStateSerializer(many=True)
    players = PlayerSerializer(many=True)

    class Meta:
        model = Game
        fields = ('id', 'turn', 'turn_stage', 'card_states', 'players',
                  'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
