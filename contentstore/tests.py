import json
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


from .models import Schedule, MessageSet


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


class TestContentStore(AuthenticatedAPITestCase):

    def make_schedule(self, minute="0", hour="1", day_of_week="*",
                      day_of_month="*", month_of_year="*"):
        schedule, created = Schedule.objects.get_or_create(
            minute=minute, hour=hour, day_of_week=day_of_week,
            day_of_month=day_of_month, month_of_year=month_of_year)
        return schedule

    def make_messageset(self, default_schedule, short_name="new set",
                        next_set=None):
        message_set, created = MessageSet.objects.get_or_create(
            short_name=short_name, next_set=next_set,
            default_schedule=default_schedule)
        return message_set

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

    def tests_update_schedule(self):
        existing_schedule = self.make_schedule()
        existing_schedule_id = existing_schedule.id
        post_data = {
            "minute": "1",
            "hour": "2",
            "day_of_week": "3",
            "day_of_month": "4",
            "month_of_year": "5",
        }
        response = self.client.put('/schedule/%s/' % existing_schedule_id,
                                   json.dumps(post_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        d = Schedule.objects.get(pk=existing_schedule_id)
        self.assertEqual(d.minute, "1")
        self.assertEqual(d.hour, "2")
        self.assertEqual(d.day_of_week, "3")
        self.assertEqual(d.day_of_month, "4")
        self.assertEqual(d.month_of_year, "5")

    def test_create_messageset(self):
        default_schedule = self.make_schedule()
        schedule_id = default_schedule.id
        post_data = {
            "short_name": "Full Set",
            "notes": "A full set of messages.",
            "default_schedule": schedule_id
        }
        response = self.client.post('/messageset/',
                                    json.dumps(post_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = MessageSet.objects.last()
        self.assertEqual(d.short_name, "Full Set")
        self.assertEqual(d.notes, "A full set of messages.")
        self.assertEqual(d.default_schedule.id, schedule_id)
        self.assertEqual(d.next_set, None)

    def test_create_messageset_missing_schedule(self):
        schedule_id = 0
        post_data = {
            "short_name": "Full Set",
            "notes": "A full set of messages.",
            "default_schedule": schedule_id
        }
        response = self.client.post('/messageset/',
                                    json.dumps(post_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_messageset_duplicate_shortname(self):
        schedule = self.make_schedule()
        self.make_messageset(default_schedule=schedule,
                             short_name="Fuller Set")
        post_data = {
            "short_name": "Fuller Set",
            "notes": "Another fuller set of messages.",
            "default_schedule": schedule.id
        }
        response = self.client.post('/messageset/',
                                    json.dumps(post_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
