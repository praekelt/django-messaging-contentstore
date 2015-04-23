import json
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


from .models import Schedule


class APITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()


class AuthenticatedAPITestCase(APITestCase):

    def setUp(self):
        super(AuthenticatedAPITestCase, self).setUp()
        self.username = 'testuser'
        self.password = 'testpass'
        self.user = User.objects.create_user(self.username,
                                             'testuser@example.com',
                                             self.password)
        token = Token.objects.create(user=self.user)
        self.token = token.key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)


class TestAnalytics(AuthenticatedAPITestCase):

    def test_login(self):
        request = self.client.post(
            '/api-token-auth/',
            {"username": "testuser", "password": "testpass"})
        token = request.data.get('token', None)
        self.assertIsNotNone(
            token, "Could not receive authentication token on login post.")
        self.assertEqual(request.status_code, 200,
                         "Status code on /auth/login was %s (should be 200)."
                         % request.status_code)

    def test_create_schedule(self):
        post_data = {
            "minute": "1",
            "hour": "2",
            "day_of_week": "3",
            "day_of_month": "4",
            "month_of_year": "5",
        }
        response = self.client.post('/schedule/',
                                    json.dumps(post_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = Schedule.objects.last()
        self.assertEqual(d.minute, "1")
        self.assertEqual(d.hour, "2")
        self.assertEqual(d.day_of_week, "3")
        self.assertEqual(d.day_of_month, "4")
        self.assertEqual(d.month_of_year, "5")
