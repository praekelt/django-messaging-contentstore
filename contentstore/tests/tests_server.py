import pkg_resources
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from contentstore.tests.tests_messageset_mixin import ContentStoreApiTestMixin
from contentstore.models import Schedule, MessageSet, Message, BinaryContent
from contentstore.serializers import (ScheduleSerializer, MessageSetSerializer,
                                      MessageSerializer)


class TestContentStore(TestCase, ContentStoreApiTestMixin):

    def setUp(self):
        self.client = self.make_client()
        self.username = 'testuser'
        self.password = 'testpass'
        self.user = User.objects.create_user(self.username,
                                             'testuser@example.com',
                                             self.password)
        token = Token.objects.create(user=self.user)
        self.token = token.key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def make_client(self):
        return APIClient()

    def make_schedule(self, minute="0", hour="1", day_of_week="*",
                      day_of_month="*", month_of_year="*"):
        schedule, created = Schedule.objects.get_or_create(
            minute=minute, hour=hour, day_of_week=day_of_week,
            day_of_month=day_of_month, month_of_year=month_of_year)
        return schedule

    def get_schedule(self, schedule_id=None):
        if schedule_id is None:
            d = Schedule.objects.last()
        else:
            d = Schedule.objects.get(pk=schedule_id)
        return ScheduleSerializer(d).data

    def make_messageset(self, default_schedule, short_name="new set",
                        next_set=None):
        message_set, created = MessageSet.objects.get_or_create(
            short_name=short_name, next_set=next_set,
            default_schedule=default_schedule)
        return message_set

    def get_messageset(self, messageset_id=None):
        if messageset_id is None:
            d = MessageSet.objects.last()
        else:
            d = MessageSet.objects.get(pk=messageset_id)
        return MessageSetSerializer(d).data

    def make_message(self, messageset, sequence_number=1, lang="eng_GB",
                     text_content="Testing 1 2 3", binary_content=None):
        message, created = Message.objects.get_or_create(
            messageset=messageset, sequence_number=sequence_number,
            lang=lang, text_content=text_content,
            binary_content=binary_content)
        return message

    def get_message(self, message_id=None):
        if message_id is None:
            d = Message.objects.last()
        else:
            d = Message.objects.get(pk=message_id)
        return MessageSerializer(d).data

    def make_binary_content(self):
        simple_png = pkg_resources.resource_stream('contentstore', 'test.png')

        post_data = {
            "content": simple_png
        }
        self.client.post('/binarycontent/',
                         post_data,
                         format='multipart',
                         )

        return BinaryContent.objects.last()
