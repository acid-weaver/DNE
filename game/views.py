from rest_framework.viewsets import ModelViewSet

from game.models import (Game,
                         Card,
                         Deck)
from game.serializers import (GameSerializer,
                              CardSerializer,
                              DeckSerialier)
from utils.permissions import AdminPermission


# TODO remove ModelViewSet to different Mixins to all used methods
# TODO customize methods with logic
class CardViewSet(ModelViewSet):
    queryset = Card.objects.order_by('name')
    serializer_class = CardSerializer


# TODO remove ModelViewSet to different Mixins to all used methods
# TODO customize methods with logic
class DeckViewSet(ModelViewSet):
    queryset = Deck.objects.order_by('id')
    serializer_class = DeckSerialier


# TODO remove ModelViewSet to different Mixins to all used methods
# TODO customize methods with logic
class GameViewSet(ModelViewSet):
    queryset = Game.objects.order_by('id')
    serializer_class = GameSerializer
    # permission_classes = [AdminPermission]
