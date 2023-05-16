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


class CardViewSet(ModelViewSet):
    queryset = Card.objects.order_by('name')
    serializer_class = CardSerializer


class DeckViewSet(ModelViewSet):
    queryset = Deck.objects.order_by('owner', 'name')
    serializer_class = DeckSerialier


class GameViewSet(ModelViewSet):
    queryset = Game.objects.order_by('id')
    serializer_class = GameSerializer

    def get_serializer_class(self):
        if self.request.method in ('POST'):
            return GameCreateSerializer
        if self.request.method in ('PUT', 'PATCH'):
            return GameUpdateSerializer
        return GameSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(self.serializer_class(instance).data, status=201, headers=headers)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(self.serializer_class(instance).data)

    # @action(detail=True, methods=['post'])
    # def assign_user(self, request):
    #     user_id = request.data.get('user_id', None)
    #     if not user_id:
    #         return Response(status=400, data='Bad Request, to add user to game you sould provide an json in following format: {"user_id":<int:id>}')


class PlayerViewSet(ModelViewSet):
    queryset = Player.objects.order_by('id')
    serializer_class = PlayerSerializer

    def get_serializer_class(self):
        if self.request.method in ('POST'):
            return PlayerCreateSerializer
        return PlayerSerializer
