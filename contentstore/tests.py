import json
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from io import BytesIO

from .models import Schedule, MessageSet, Message, BinaryContent


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

    def make_message(self, messageset, sequence_number=1, lang="eng_GB",
                     text_content="Testing 1 2 3", binary_content=None):
        message, created = Message.objects.get_or_create(
            messageset=messageset, sequence_number=sequence_number,
            lang=lang, text_content=text_content,
            binary_content=binary_content)
        return message

    def make_binary_content(self):
        # models.generate_new_filename = lambda *a: "20151201010101012345.png"
        simple_png = BytesIO(
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc````\x00\x00\x00\x05\x00\x01\xa5\xf6E@\x00\x00\x00\x00IEND\xaeB`\x82')   # flake8: noqa
        simple_png.name = 'test.png'

        post_data = {
            "content": simple_png
        }
        self.client.post('/binarycontent/',
                         post_data,
                         format='multipart',
                         )

        return BinaryContent.objects.last()

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
        patch_data = {
            "minute": "1",
            "hour": "2",
            "day_of_week": "3",
            "day_of_month": "4",
            "month_of_year": "5",
        }
        response = self.client.put('/schedule/%s/' % existing_schedule_id,
                                   json.dumps(patch_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        d = Schedule.objects.get(pk=existing_schedule_id)
        self.assertEqual(d.minute, "1")
        self.assertEqual(d.hour, "2")
        self.assertEqual(d.day_of_week, "3")
        self.assertEqual(d.day_of_month, "4")
        self.assertEqual(d.month_of_year, "5")

    def tests_delete_schedule(self):
        existing_schedule = self.make_schedule()
        existing_schedule_id = existing_schedule.id
        response = self.client.delete('/schedule/%s/' % existing_schedule_id,
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        check = Schedule.objects.filter(id=existing_schedule_id).count()
        self.assertEqual(check, 0)

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

    def test_update_messageset(self):
        schedule = self.make_schedule()
        default_messageset = self.make_messageset(default_schedule=schedule,
                                                  short_name="Full Set")
        default_messageset_id = default_messageset.id
        patch_data = {
            "notes": "A full set of messages with more notes."
        }
        response = self.client.patch('/messageset/%s/' % default_messageset_id,
                                     json.dumps(patch_data),
                                     content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        d = MessageSet.objects.get(pk=default_messageset_id)
        self.assertEqual(d.short_name, "Full Set")
        self.assertEqual(d.notes, "A full set of messages with more notes.")

    def tests_delete_messageset(self):
        schedule = self.make_schedule()
        default_messageset = self.make_messageset(default_schedule=schedule,
                                                  short_name="Full Set")
        default_messageset_id = default_messageset.id
        response = self.client.delete('/messageset/%s/' %
                                      (default_messageset_id, ),
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        check = MessageSet.objects.filter(id=default_messageset_id).count()
        self.assertEqual(check, 0)

    def test_create_message_text(self):
        schedule = self.make_schedule()
        messageset = self.make_messageset(default_schedule=schedule,
                                          short_name="Full Set")
        post_data = {
            "messageset": messageset.id,
            "sequence_number": 2,
            "lang": "afr_ZA",
            "text_content": "Message two"
        }
        response = self.client.post('/message/',
                                    json.dumps(post_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = Message.objects.last()
        self.assertEqual(d.messageset, messageset)
        self.assertEqual(d.sequence_number, 2)
        self.assertEqual(d.lang, "afr_ZA")
        self.assertEqual(d.text_content, "Message two")

    def test_update_message_text(self):
        schedule = self.make_schedule()
        messageset = self.make_messageset(default_schedule=schedule,
                                          short_name="Full Set")
        message = self.make_message(messageset)
        message_id = message.id
        patch_data = {
            "text_content": "Message one updated"
        }
        response = self.client.patch('/message/%s/' % message_id,
                                     json.dumps(patch_data),
                                     content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        d = Message.objects.get(pk=message_id)
        self.assertEqual(d.text_content, "Message one updated")

    def tests_delete_message_text(self):
        schedule = self.make_schedule()
        messageset = self.make_messageset(default_schedule=schedule,
                                          short_name="Full Set")
        message = self.make_message(messageset)
        message_id = message.id
        response = self.client.delete('/message/%s/' % message_id,
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        check = Message.objects.filter(id=message_id).count()
        self.assertEqual(check, 0)

    def test_create_binary_content(self):
        simple_png = BytesIO(
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc````\x00\x00\x00\x05\x00\x01\xa5\xf6E@\x00\x00\x00\x00IEND\xaeB`\x82')   # flake8: noqa
        simple_png.name = 'test.png'

        post_data = {
            "content": simple_png
        }
        response = self.client.post('/binarycontent/',
                                    post_data,
                                    format='multipart',
                                    )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = BinaryContent.objects.last()
        self.assertEqual(d.content.name.split('.')[-1], 'png')

    def tests_delete_binary_content(self):
        binarycontent = self.make_binary_content()
        binarycontent_id = binarycontent.id
        response = self.client.delete('/binarycontent/%s/' % binarycontent_id,
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        check = BinaryContent.objects.filter(id=binarycontent_id).count()
        self.assertEqual(check, 0)

    def test_create_message_binary(self):
        schedule = self.make_schedule()
        messageset = self.make_messageset(default_schedule=schedule,
                                          short_name="Full Set")
        binarycontent = self.make_binary_content()
        binarycontent_id = binarycontent.id
        post_data = {
            "messageset": messageset.id,
            "sequence_number": 2,
            "lang": "afr_ZA",
            "binary_content": binarycontent_id
        }
        response = self.client.post('/message/',
                                    json.dumps(post_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = Message.objects.last()
        self.assertEqual(d.messageset, messageset)
        self.assertEqual(d.sequence_number, 2)
        self.assertEqual(d.lang, "afr_ZA")
        self.assertEqual(d.binary_content.content.name.split('.')[-1], 'png')

    def test_create_message_binary_and_text(self):
        schedule = self.make_schedule()
        messageset = self.make_messageset(default_schedule=schedule,
                                          short_name="Full Set")
        binarycontent = self.make_binary_content()
        binarycontent_id = binarycontent.id
        post_data = {
            "messageset": messageset.id,
            "sequence_number": 2,
            "lang": "afr_ZA",
            "text_content": "Message two",
            "binary_content": binarycontent_id
        }
        response = self.client.post('/message/',
                                    json.dumps(post_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = Message.objects.last()
        self.assertEqual(d.messageset, messageset)
        self.assertEqual(d.sequence_number, 2)
        self.assertEqual(d.lang, "afr_ZA")
        self.assertEqual(d.binary_content.content.name.split('.')[-1], 'png')
        self.assertEqual(d.text_content, "Message two")

    def test_create_message_no_content_rejected(self):
        schedule = self.make_schedule()
        messageset = self.make_messageset(default_schedule=schedule,
                                          short_name="Full Set")
        post_data = {
            "messageset": messageset.id,
            "sequence_number": 2,
            "lang": "afr_ZA"
        }
        response = self.client.post('/message/',
                                    json.dumps(post_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_message_content(self):
        schedule = self.make_schedule()
        messageset = self.make_messageset(default_schedule=schedule,
                                          short_name="Full Set")
        binarycontent = self.make_binary_content()
        message = self.make_message(messageset=messageset,
                                    text_content="Message two",
                                    binary_content=binarycontent)

        response = self.client.get('/message/%s/content' % message.id,
                                   content_type='application/json')
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content["binary_content"]["id"], binarycontent.id)
        self.assertEqual(content["text_content"], message.text_content)
        self.assertEqual(content["lang"], message.lang)
        self.assertEqual(content["messageset"], messageset.id)
        self.assertEqual(
            content["sequence_number"], message.sequence_number)
        self.assertEqual("created_at" in content, True)
        self.assertEqual("updated_at" in content, True)
        self.assertEqual("id" in content, True)

    def test_get_messageset_messages_content(self):
        schedule = self.make_schedule()
        messageset = self.make_messageset(default_schedule=schedule,
                                          short_name="Three Message Set")
        binarycontent = self.make_binary_content()
        message2 = self.make_message(messageset=messageset,
                                     text_content="Message two",
                                     sequence_number=2,
                                     binary_content=binarycontent)
        message1 = self.make_message(messageset=messageset,
                                     sequence_number=1,
                                     text_content="Message one",
                                     binary_content=binarycontent)
        message3 = self.make_message(messageset=messageset,
                                     sequence_number=3,
                                     text_content="Message three",
                                     binary_content=binarycontent)

        response = self.client.get('/messageset/%s/messages' % messageset.id,
                                   content_type='application/json')
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content["short_name"], "Three Message Set")
        self.assertEqual(len(content["messages"]), 3)
        messages = content["messages"]  # They should be sorted by seq num now
        self.assertEqual(messages[0]["binary_content"]["id"], binarycontent.id)
        self.assertEqual(messages[0]["text_content"], "Message one")
        self.assertEqual(messages[0]["id"], message1.id)
        self.assertEqual(messages[1]["id"], message2.id)
        self.assertEqual(messages[2]["id"], message3.id)
