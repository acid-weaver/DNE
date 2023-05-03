from django.db import models

from utils.models import TimeStamps
from user.models import User


class Card(TimeStamps):
    """
    Game card.
    """

    NPC = 1
    CLASS = 2
    LOOT = 3
    SOUND = 4
    PROJECT = 5
    DIA = 6
    ANTI = 7

    CARD_TYPES = [
        (NPC, 'NPC'),
        (CLASS, 'player class'),
        (LOOT, 'loot'),
        (SOUND, 'sound'),
        (PROJECT, 'project'),
        (DIA, 'doing'),
        (ANTI, 'anti')
    ]

    name = models.CharField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True)
    type = models.PositiveSmallIntegerField(choices=CARD_TYPES)
    bonus = models.PositiveSmallIntegerField(default=1)

    buy_price = models.PositiveIntegerField(blank=True, null=True)
    rent_price = models.PositiveIntegerField(blank=True, null=True)

    sp_per_usage = models.SmallIntegerField(default=0)


class Deck(TimeStamps):
    """
    Cards deck, that can be used in game.
    """

    name = models.CharField(max_length=255, db_index=True)
    cards = models.ManyToManyField(Card, related_name='decks')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decks')

    class Meta:
        unique_together = ('name', 'owner')


class Game(TimeStamps):
    """
    Game instance.
    """

    CREATED = 0
    FIRST = 1
    DECISION = 2
    TURN = 3
    CALCULATE = 4
    FREE_TIME = 5

    TURN_STAGES = [
        (CREATED, 'created'),
        (FIRST, 'first'),
        (DECISION, 'decision'),
        (TURN, 'making sound'),
        (CALCULATE, 'calculating income'),
        (FREE_TIME, 'free time after party'),
    ]

    turn = models.PositiveSmallIntegerField(default=0)
    turn_stage = models.PositiveSmallIntegerField(default=CREATED, choices=TURN_STAGES)


class Player(models.Model):
    """
    Player in game.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playing')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='players')

    lvl = models.PositiveSmallIntegerField(default=1)
    energy = models.PositiveSmallIntegerField(default=40)
    bankroll = models.PositiveIntegerField(default=12000)
    sp = models.PositiveSmallIntegerField(default=3)

    class Meta:
        unique_together = ('game', 'user')


class CardState(models.Model):
    """
    State of every card from deck of the game.
    """

    HAND = 1
    TABLE = 2
    IN_DECK = 3

    STATES = [
        (HAND, 'in hand'),
        (TABLE, 'card at the table'),
        (IN_DECK, 'card currently in deck'),
    ]

    DEFAULT = 1
    RENTED = 2
    BUYED = 3

    DESCRIPTIONS = [
        (DEFAULT, 'commonly'),
        (RENTED, 'card in rent'),
        (BUYED, "card in owner's hand")
    ]

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='card_states')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='states')

    player = models.ForeignKey(Player, on_delete=models.SET_NULL, blank=True, null=True, related_name='cards')
    owner = models.ForeignKey(Player, on_delete=models.SET_NULL, blank=True, null=True, related_name='own_cards')

    state = models.PositiveSmallIntegerField(default=IN_DECK, choices=STATES)
    state_description = models.PositiveSmallIntegerField(default=DEFAULT, choices=DESCRIPTIONS)
    buy_price = models.PositiveIntegerField(blank=True, null=True)
    rent_price = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('game', 'card')
