from django.contrib import admin

from game.models import Card, Game, CardState, Player


class CardInline(admin.StackedInline):
    model = Card
    extra = 1


class PlayerInline(admin.StackedInline):
    model = Player
    extra = 1


class CardStateInline(admin.StackedInline):
    model = CardState
    extra = 1

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name')


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'turn', 'turn_stage')
    list_filter = ('turn', 'turn_stage')
    search_fields = ('id',)
    # inlines = (PlayerInline,)


@admin.register(CardState)
class CardStateAdmin(admin.ModelAdmin):
    list_display = ('id', 'game', 'card', 'player', 'owner')
    list_display_links = ('id', 'game', 'card')
    list_filter = ('game',)
    search_fields = ('id', 'game__id')
    # inlines = (CardInline,)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'game')
    list_display_links = ('id', 'user', 'game')
    list_filter = ('game',)
    search_fields = ('id', 'user__username')
