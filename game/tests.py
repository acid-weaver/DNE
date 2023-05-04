import random
from rest_framework.renderers import JSONRenderer
from utils.tests import BaseTestCaseAPI
from model_bakery import baker
from rest_framework.reverse import reverse

from game.models import Card, Game, Player, CardState
from game.serializers import CardSerializer, CardStateSerializer, PlayerSerializer
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

        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Card.objects.count())

        body['name'] = 'test card 2'
        response = self.admin_client.post(url, body)

        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Card.objects.count())

        body['name'] = 'test card 3'
        response = self.admin_client.post(url, body)

        card_id = response.data['id']
        url = reverse("card-detail", [card_id,])
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, 200)

        test_instance = dict(body)
        test_instance['buy_price'] = None
        test_instance['rent_price'] = None
        response_instance = remove_timestamps_id(response.data)
        self.assertEqual(response_instance, test_instance)
        

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
        players = response.data.get('players', [])
        card_states = response.data.get('card_states', [])
        self.assertEqual(players, [i[0] for i in Player.objects.filter(game_id=game_id).values_list('id')])
        self.assertEqual(card_states, [i[0] for i in CardState.objects.filter(game_id=game_id).values_list('id')])

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
        players = response.data.get('players', [])
        card_states = response.data.get('card_states', [])
        self.assertEqual(players, [k[0] for k in Player.objects.filter(game_id=game_id).values_list('id')])
        self.assertEqual(card_states, [k[0] for k in CardState.objects.filter(game_id=game_id).values_list('id')])
