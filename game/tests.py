import json
import random
from rest_framework.renderers import JSONRenderer
from utils.tests import BaseTestCaseAPI
from model_bakery import baker
from rest_framework.reverse import reverse

from game.models import Card, Game, Player, CardState
from game.serializers import (CardSerializer, CardStateSerializer, PlayerSerializer,
                              GameSerializer)
from user.models import User
from user.serializers import UserSerializer
from utils.tests import remove_timestamps_id


class TestCard(BaseTestCaseAPI):

    def test_card_create(self):
        body = {
            'name': 'test card 1',
            'description': 'this is test card 01',
            'type': Card.ANTI,
            'bonus': 0,
            # 'buy_price': None,
            # 'rent_price': None,
            'sp_per_usage': 0
        }
        url = reverse("card-list")
        response = self.admin_client.post(url, body)

        self.assertEqual(response.status_code, 201)
        test_instance = dict(body)
        test_instance['buy_price'] = None
        test_instance['rent_price'] = None
        response_instance = remove_timestamps_id(response.data)
        self.assertEqual(response_instance, test_instance)

        # with same name
        response = self.admin_client.post(url, body)
        self.assertEqual(response.status_code, 400)

    def test_card_update(self):
        body = {
            'name': 'test card 1',
            'description': 'this is test card 01',
            'type': Card.ANTI,
            'bonus': 0,
            # 'buy_price': None,
            # 'rent_price': None,
            'sp_per_usage': 0
        }
        url = reverse("card-list")
        response = self.admin_client.post(url, body)
        self.assertEqual(response.status_code, 201)

        card_id = response.data['id']
        body['buy_price'] = 1000
        body['rent_price'] = 10
        url = reverse("card-detail", [card_id,])

        response = self.admin_client.put(url, body)
        self.assertEqual(response.status_code, 200)
        response_instance = remove_timestamps_id(response.data)
        self.assertEqual(response_instance, body)

        # partial update
        test_instance = dict(body)
        test_instance['buy_price'] = 9999
        test_instance['rent_price'] = 99
        body = {
            'buy_price': 9999,
            'rent_price': 99,
        }

        response = self.admin_client.patch(url, body)
        self.assertEqual(response.status_code, 200)
        response_instance = remove_timestamps_id(response.data)
        self.assertEqual(response_instance, test_instance)
        # print(response.status_code)
        # print(response.data)

    def test_card_get(self):
        # list
        baker.make(Card, _quantity=random.randrange(2, 4, 1))
        url = reverse("card-list")

        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Card.objects.count())

        baker.make(Card, _quantity=random.randrange(2, 4, 1))

        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Card.objects.count())

        # retrieve
        card = baker.make(Card)
        url = reverse("card-detail", [card.id])

        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, 200)
        test_instance = CardSerializer(card).data
        self.assertEqual(response.data, test_instance)
        

class TestGame(BaseTestCaseAPI):

    def test_game_create(self):
        # creation with format of list of ints
        card_ids = [baker.make(Card).id for _ in range(random.randrange(9, 19, 1))]
        user_ids = [baker.make(User).id for _ in range(random.randrange(3, 7, 1))]
        body = {
            "cards": card_ids,
            "users": user_ids
        }

        url = reverse("game-list")
        response = self.admin_client.post(url, body)
        self.assertEqual(response.status_code, 201)

        game_id = response.data.get("id", None)
        url = reverse("game-detail", [game_id])
        response = self.admin_client.get(url)

        players = response.data.get('players', [])
        card_states = response.data.get('card_states', [])
        self.assertEqual(players, [PlayerSerializer(player).data for player in Player.objects.filter(game_id=game_id)])
        self.assertEqual(card_states, [CardStateSerializer(card).data for card in CardState.objects.filter(game_id=game_id)])

        # creation with format list of json - cards
        cards = [JSONRenderer().render(CardSerializer(card).data) for card in [Card.objects.get(id=card_id) for card_id in card_ids]]
        users = [JSONRenderer().render(UserSerializer(user).data) for user in [User.objects.get(id=user_id) for user_id in user_ids]]
        body = {
            "cards": cards,
            "users": users
        }

        url = reverse("game-list")
        response = self.admin_client.post(url, body)
        self.assertEqual(response.status_code, 201)

        game_id = response.data.get("id", None)
        url = reverse("game-detail", [game_id])
        response = self.admin_client.get(url)

        players = response.data.get('players', [])
        card_states = response.data.get('card_states', [])
        self.assertEqual(players, [PlayerSerializer(player).data for player in Player.objects.filter(game_id=game_id)])
        self.assertEqual(card_states, [CardStateSerializer(card).data for card in CardState.objects.filter(game_id=game_id)])

    def test_game_update(self):
        card_states = baker.make(CardState, _quantity=random.randrange(9, 19, 1))
        players_count = random.randrange(3, 7, 1)
        players = baker.make(Player, _quantity=players_count)
        game = baker.make(Game, players=players, card_states=card_states)

        # info with witch we would update card_states
        card_ids = []
        updated_card_states = []
        for card_state in card_states:

            updated_card_state = CardStateSerializer(card_state).data
            updated_card_state['id'] = card_state.id
            updated_card_state['card'] = updated_card_state['card']['id']
            updated_card_state['player'] = players[random.randrange(0, players_count-1, 1)].id
            updated_card_state['owner'] = players[random.randrange(0, players_count-1, 1)].id
            updated_card_state['state'] = random.randrange(1, 3, 1)
            updated_card_state['state_description'] = random.randrange(1, 3, 1)

            if updated_card_state['buy_price']:
                updated_card_state['buy_price'] = random.randrange(10000, 50000, 1)

            if updated_card_state['rent_price']:
                updated_card_state['rent_price'] = random.randrange(1000, 5000, 1)

            card_ids.append(card_state.id)
            updated_card_states.append(JSONRenderer().render(updated_card_state))

        # info with which we would update players
        user_ids = []
        updated_players = []
        for player in players:
            updated_player = PlayerSerializer(player).data
            updated_player['id'] = player.id
            # updated_player['user'] = updated_player['user']['id']
            updated_player['lvl'] = random.randrange(1, 9, 1)
            updated_player['energy'] = random.randrange(1, 40, 1)
            updated_player['bankroll'] = random.randrange(1, 100000, 1)
            updated_player['sp'] = random.randrange(0, 9, 1)

            user_ids.append(player.id)
            updated_players.append(JSONRenderer().render(updated_player))

        updated_game = GameSerializer(game).data
        updated_game["card_states"] = updated_card_states
        updated_game["players"] = updated_players
        updated_game["cards"] = card_ids
        updated_game["users"] = user_ids

        url = reverse("game-detail", [game.id])

        response = self.admin_client.put(url, updated_game)
        self.assertEqual(response.status_code, 200)

        game_id = response.data.get("id", None)
        url = reverse("game-detail", [game_id])

        response = self.admin_client.get(url)

        players = response.data.get('players', [])
        card_states = response.data.get('card_states', [])
        self.assertEqual(players, [PlayerSerializer(player).data for player in Player.objects.filter(game_id=game_id)])
        self.assertEqual(card_states, [CardStateSerializer(card).data for card in CardState.objects.filter(game_id=game_id)])

        for count in range(len(updated_players)):

            self.assertEqual(dict(players[count]), json.loads(updated_players[count]))

            card_state = dict(card_states[count])
            card_state['card'] = card_state['card']['id']
            self.assertEqual(card_state, json.loads(updated_card_states[count]))

    def test_game_append_players(self):
        # Create an existing game with some card states and players
        game = baker.make(Game)
        card_states = baker.make(CardState, game=game, _quantity=random.randrange(9, 19, 1))
        players = baker.make(Player, game=game, _quantity=random.randrange(3, 5, 1))
        users = baker.make(User, _quantity=2)

        # Generate data for new players to be appended
        new_players_data = [
            {
                'user': users[0].id,
                'game': game.id,
                'lvl': random.randrange(1, 9, 1),
                'energy': random.randrange(1, 40, 1),
                'bankroll': random.randrange(1, 100000, 1),
                'sp': random.randrange(0, 9, 1),
            },
            {
                'user': users[1].id,
                'game': game.id,
                'lvl': random.randrange(1, 9, 1),
                'energy': random.randrange(1, 40, 1),
                'bankroll': random.randrange(1, 100000, 1),
                'sp': random.randrange(0, 9, 1),
            },
        ]

        url = reverse("game-detail", [game.id])

        body = {'players': new_players_data}
        response = self.admin_client.patch(url, body, format='json')
        self.assertEqual(response.status_code, 200)

        game_id = response.data.get("id", None)
        url = reverse("game-detail", [game_id])

        response = self.admin_client.get(url)

        players = response.data.get('players', [])
        card_states = response.data.get('card_states', [])

        self.assertEqual(players, [PlayerSerializer(player).data for player in Player.objects.filter(game_id=game_id)])

        # Assert that the new players are appended
        users = [user.id for user in users]
        new_players = Player.objects.filter(game_id=game_id, user_id__in=users)
        self.assertEqual(len(new_players), len(new_players_data))
        for i, new_player in enumerate(new_players):
            self.assertEqual(new_player.user.id, new_players_data[i]['user'])
            self.assertEqual(new_player.lvl, new_players_data[i]['lvl'])
            self.assertEqual(new_player.energy, new_players_data[i]['energy'])
            self.assertEqual(new_player.bankroll, new_players_data[i]['bankroll'])
            self.assertEqual(new_player.sp, new_players_data[i]['sp'])

        # Assert that the existing card states remain unchanged
        self.assertEqual(card_states, [CardStateSerializer(card_state).data for card_state in CardState.objects.filter(game_id=game_id)])


class PlayerCreationTest(BaseTestCaseAPI):

    def test_create_player(self):
        user = baker.make(User)
        game = baker.make(Game)

        # Prepare the request data
        data = {
            "user": user.id,
            "game": game.id,
            "lvl": random.randrange(1, 9, 1),
            "energy": random.randrange(1, 40, 1),
            "bankroll": random.randrange(1, 100000, 1),
            "sp": random.randrange(0, 9, 1),
        }

        # Send the POST request to create the player
        url = reverse("player-list")
        response = self.client.post(url, data)

        # Assert the response status code
        self.assertEqual(response.status_code, 201)

        # Assert the player object was created
        player = Player.objects.get(id=response.data["id"])
        self.assertEqual(player.user, user)
        self.assertEqual(player.lvl, data["lvl"])
        self.assertEqual(player.energy, data["energy"])
        self.assertEqual(player.bankroll, data["bankroll"])
        self.assertEqual(player.sp, data["sp"])
