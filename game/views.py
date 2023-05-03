from rest_framework.viewsets import ModelViewSet

from game.models import (Card,
                         Deck,
                         Game,
                         Player)
from game.serializers import (CardSerializer,
                              DeckSerialier,
                              GameCreateSerializer,
                              GameSerializer,
                              PlayerSerializer)
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
        if self.request.method == 'POST':
            return GameCreateSerializer
        return GameSerializer


# TODO remove ModelViewSet to different Mixins to all used methods
# TODO customize methods with logic
class PlayerViewSet(ModelViewSet):
    queryset = Player.objects.order_by('id')
    serializer_class = PlayerSerializer
