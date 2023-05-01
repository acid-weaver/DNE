from django.urls import path

from game.views import (GameViewSet,
                        CardViewSet,
                        DeckViewSet)


game_list = GameViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

game_detail = GameViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

card_list = CardViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

card_detail = CardViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

deck_list = DeckViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

deck_detail = DeckViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})


urlpatterns = [
    path('games/', game_list, name='game-list'),
    path('game/<int:pk>/', game_detail, name='game-detail'),

    path('cards/', card_list, name='card-list'),
    path('card/<int:pk>/', card_detail, name='card-detail'),

    path('decks/', deck_list, name='deck-list'),
    path('deck/<int:pk>/', deck_detail, name='deck-detail'),
]
