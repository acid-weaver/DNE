from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from game.models import (Card,
                         Deck,
                         Game,
                         Player)
from game.serializers import (CardSerializer,
                              DeckSerialier,
                              GameCreateSerializer,
                              GameUpdateSerializer,
                              GameSerializer,
                              PlayerSerializer,
                              PlayerCreateSerializer)
from utils.permissions import AdminPermission


# TODO remove ModelViewSet to different Mixins to all used methods
# TODO customize methods with logic
class CardViewSet(ModelViewSet):
    queryset = Card.objects.order_by('name')
    serializer_class = CardSerializer


# TODO remove ModelViewSet to different Mixins to all used methods
# TODO customize methods with logic
class DeckViewSet(ModelViewSet):
    queryset = Deck.objects.order_by('owner', 'name')
    serializer_class = DeckSerialier


# TODO remove ModelViewSet to different Mixins to all used methods
# TODO customize methods with logic
class GameViewSet(ModelViewSet):
    queryset = Game.objects.order_by('id')
    serializer_class = GameSerializer


    def get_serializer_class(self):
        if self.request.method in ('POST'):
            return GameCreateSerializer
        if self.request.method in ('PUT', 'PATCH'):
            return GameUpdateSerializer
        return GameSerializer


    # @action(detail=True, methods=['post'])
    # def assign_user(self, request):
    #     user_id = request.data.get('user_id', None)
    #     if not user_id:
    #         return Response(status=400, data='Bad Request, to add user to game you sould provide an json in following format: {"user_id":<int:id>}')


# TODO remove ModelViewSet to different Mixins to all used methods
# TODO customize methods with logic
class PlayerViewSet(ModelViewSet):
    queryset = Player.objects.order_by('id')
    serializer_class = PlayerSerializer

    def get_serializer_class(self):
        if self.request.method in ('POST'):
            return PlayerCreateSerializer
        return PlayerSerializer
