from rest_framework.authtoken.models import Token
from rest_framework.test import RequestsClient
from django.test import TransactionTestCase
from django.contrib.auth.models import User
from .models import Lake, FishCatch

class GraphQLAuthTestCase(TransactionTestCase):


    def seed_user(self):
        self.password = 's3cret123!#@'
        user = User.objects.create_user(
            username='colan',
            email='cconnon11@gmail.com',
            password=self.password
        )
        return user

    def test_it_can_grab_token(self):
        client = RequestsClient()
        user = self.seed_user()
        response = client.post(
            'http://localhost/token',
            json={
                'username': user.username,
                'password': self.password
            }
        )
        print(response.json())
        self.assertEqual(response.json()['token'], str(Token.objects.get(user=user)))
        # self.assertTrue(False)

    def test_it_only_fetches_user_objects(self):
        client = RequestsClient()
        user = self.seed_user()
        lake = Lake.objects.create(
            name='Lake',
            user=user
        )
        response = client.post(
            'http://localhost/token',
            json={
                'username': user.username,
                'password': self.password
            }
        )
        query = '''
        {
            allLakes{
                id
                name
            }
        }
        '''
        data = {'query': query}
        graphql = client.post(
            'http://localhost/graphql',
            json=data,
            headers={'Authorization': 'Token {}'.format(response.json()['token'])}
        )
        self.assertEquals(int(graphql.json()['data']['allLakes'][0]['id']), lake.id)
        self.assertEquals(len(graphql.json()['data']['allLakes']), 1)

        user1 = User.objects.create_user(
            username='colan1',
            email='cconnon111@gmail.com',
            password=self.password
        )
        lake2 = Lake.objects.create(
            name='Lake',
            user=user1
        )
        graphql = client.post(
            'http://localhost/graphql',
            json=data,
            headers={'Authorization': 'Token {}'.format(response.json()['token'])}
        )
        self.assertEquals(len(graphql.json()['data']['allLakes']), 1)
