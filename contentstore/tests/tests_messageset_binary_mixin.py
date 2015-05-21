import json
import pkg_resources
from rest_framework import status


class ContentStoreBinaryApiTestMixin(object):

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

    def test_create_binary_content(self):
        simple_png = pkg_resources.resource_stream('contentstore', 'test.png')

        post_data = {
            "content": simple_png
        }
        response = self.client.post('/binarycontent/',
                                    post_data,
                                    format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = self.get_binary_content()
        self.assertEqual(d["content"].split('.')[-1], 'png')

    def tests_delete_binary_content(self):
        binarycontent = self.make_binary_content()
        binarycontent_id = binarycontent.id
        response = self.client.delete('/binarycontent/%s/' % binarycontent_id,
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        check = self.get_binary_contents()
        self.assertEqual(len(check), 0)

    def test_create_message_binary(self):
        schedule = self.make_schedule()
        messageset = self.make_messageset(default_schedule=schedule.id,
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

        d = self.get_message()
        self.assertEqual(d["messageset"], messageset.id)
        self.assertEqual(d["sequence_number"], 2)
        self.assertEqual(d["lang"], "afr_ZA")
        self.assertEqual(d["binary_content"], binarycontent_id)

    def test_create_message_binary_and_text(self):
        schedule = self.make_schedule()
        messageset = self.make_messageset(default_schedule=schedule.id,
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

        d = self.get_message()
        self.assertEqual(d["messageset"], messageset.id)
        self.assertEqual(d["sequence_number"], 2)
        self.assertEqual(d["lang"], "afr_ZA")
        self.assertEqual(d["binary_content"], binarycontent_id)
        self.assertEqual(d["text_content"], "Message two")

    def test_create_message_no_content_rejected(self):
        schedule = self.make_schedule()
        messageset = self.make_messageset(default_schedule=schedule.id,
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
        messageset = self.make_messageset(default_schedule=schedule.id,
                                          short_name="Full Set")
        binarycontent = self.make_binary_content()
        message = self.make_message(messageset=messageset.id,
                                    text_content="Message two",
                                    binary_content=binarycontent.id)

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
        messageset = self.make_messageset(default_schedule=schedule.id,
                                          short_name="Three Message Set")
        binarycontent = self.make_binary_content()
        message2 = self.make_message(messageset=messageset.id,
                                     text_content="Message two",
                                     sequence_number=2,
                                     binary_content=binarycontent.id)
        message1 = self.make_message(messageset=messageset.id,
                                     sequence_number=1,
                                     text_content="Message one",
                                     binary_content=binarycontent.id)
        message3 = self.make_message(messageset=messageset.id,
                                     sequence_number=3,
                                     text_content="Message three",
                                     binary_content=binarycontent.id)

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
