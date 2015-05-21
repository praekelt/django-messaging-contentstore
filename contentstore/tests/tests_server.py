import pkg_resources
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.utils import six
from django.conf import settings
from rest_framework.settings import api_settings
from rest_framework.compat import force_bytes_or_smart_bytes


from contentstore.tests.tests_messageset_mixin import ContentStoreApiTestMixin
from contentstore.tests.tests_messageset_binary_mixin import (
    ContentStoreBinaryApiTestMixin)
from contentstore.models import Schedule, MessageSet, Message, BinaryContent
from contentstore.serializers import (ScheduleSerializer, MessageSetSerializer,
                                      MessageSerializer,
                                      BinaryContentSerializer)


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

    def get_schedules(self):
        d = Schedule.objects.all()
        s = []
        for schedule in d:
            s.append(ScheduleSerializer(schedule).data)
        return s

    def make_messageset(self, default_schedule, short_name="new set",
                        next_set=None):
        message_set, created = MessageSet.objects.get_or_create(
            short_name=short_name, next_set=next_set,
            default_schedule_id=default_schedule)
        return message_set

    def get_messageset(self, messageset_id=None):
        if messageset_id is None:
            d = MessageSet.objects.last()
        else:
            d = MessageSet.objects.get(pk=messageset_id)
        return MessageSetSerializer(d).data

    def get_messagesets(self):
        d = MessageSet.objects.all()
        s = []
        for messageset in d:
            s.append(MessageSetSerializer(messageset).data)
        return s

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

    def get_messages(self):
        d = Message.objects.all()
        s = []
        for message in d:
            s.append(MessageSerializer(message).data)
        return s


class FakeResponse(object):

    def __init__(self, status_code, data, body):
        self.status_code = status_code
        self.data = data
        self.content = body


class Struct:

    def __init__(self, **entries):
        self.__dict__.update(entries)


class FakeClient(object):

    renderer_classes_list = api_settings.TEST_REQUEST_RENDERER_CLASSES
    default_format = api_settings.TEST_REQUEST_DEFAULT_FORMAT

    def __init__(self, api, req_class, headers=None):
        super(FakeClient, self).__init__()
        self.renderer_classes = {}
        for cls in self.renderer_classes_list:
            self.renderer_classes[cls.format] = cls
        self.api = api
        self.req_class = req_class
        if headers is None:
            headers = {}
        self.headers = headers

    def _encode_data(self, data, format=None, content_type=None):
        """
        Encode the data returning a two tuple of (bytes, content_type)
        """

        if data is None:
            return ('', content_type)

        assert format is None or content_type is None, (
            'You may not set both `format` and `content_type`.'
        )

        if content_type:
            # Content type specified explicitly, treat data as a raw bytestring
            ret = force_bytes_or_smart_bytes(data, settings.DEFAULT_CHARSET)

        else:
            format = format or self.default_format

            assert format in self.renderer_classes, (
                "Invalid format '{0}'. Available formats are {1}. "
                "Set TEST_REQUEST_RENDERER_CLASSES to enable "
                "extra request formats.".format(
                    format,
                    ', '.join(
                        ["'" + fmt + "'" for fmt in
                            self.renderer_classes.keys()])
                )
            )

            # Use format and render the data into a bytestring
            renderer = self.renderer_classes[format]()
            ret = renderer.render(data)

            # Determine the content-type header from the renderer
            content_type = "{0}; charset={1}".format(
                renderer.media_type, renderer.charset
            )

            # Coerce text to bytes if required.
            if isinstance(ret, six.text_type):
                ret = bytes(ret.encode(renderer.charset))

        return ret, content_type

    def get(self, path, data=None, content_type=None):
        # TODO: no filter support at the moment
        self.headers["Content-Type"] = content_type
        resp = self.api.handle_request(
            self.req_class('GET', path, None, self.headers))
        return FakeResponse(resp.code, resp.data, resp.body)

    def post(self, path, data=None, format=None, content_type=None):
        data, content_type = self._encode_data(data, format, content_type)
        self.headers["Content-Type"] = content_type
        resp = self.api.handle_request(self.req_class('POST', path, data,
                                                      self.headers))
        return FakeResponse(resp.code, resp.data, resp.body)

    def put(self, path, data=None, format=None, content_type=None):
        data, content_type = self._encode_data(data, format, content_type)
        self.headers["Content-Type"] = content_type
        resp = self.api.handle_request(self.req_class('PUT', path, data,
                                                      self.headers))
        return FakeResponse(resp.code, resp.data, resp.body)

    def patch(self, path, data=None, format=None, content_type=None):
        data, content_type = self._encode_data(data, format, content_type)
        self.headers["Content-Type"] = content_type
        resp = self.api.handle_request(self.req_class('PATCH', path, data,
                                                      self.headers))
        return FakeResponse(resp.code, resp.data, resp.body)

    def delete(self, path, data=None, format=None, content_type=None):
        data, content_type = self._encode_data(data, format, content_type)
        self.headers["Content-Type"] = content_type
        resp = self.api.handle_request(self.req_class('DELETE', path, data,
                                                      self.headers))
        return FakeResponse(resp.code, resp.data, resp.body)

    def options(self, path, data=None, format=None, content_type=None):
        data, content_type = self._encode_data(data, format, content_type)
        self.headers["Content-Type"] = content_type
        resp = self.api.handle_request(self.req_class('OPTIONS', path, data,
                                                      self.headers))
        return FakeResponse(resp.code, resp.data, resp.body)


class TestFakeContentStore(TestCase, ContentStoreApiTestMixin):

    def setUp(self):
        try:
            from verified_fake.fake_contentstore import (Request,
                                                         FakeContentStoreApi)
        except ImportError as err:
            if "verified_fake" not in err.args[0]:
                raise
            raise ImportError(" ".join([
                err.args[0],
                "(install from pypi or the 'verified_fake' directory)"]))

        self.req_class = Request
        self.api_class = FakeContentStoreApi
        self.api = self.api_class("", "token-1", {}, {}, {}, {})
        self.client = self.make_client()

    def make_client(self):
        client = FakeClient(self.api, self.req_class,
                            {"Authorization": "Token token-1"})
        return client

    def make_schedule(self, minute="0", hour="1", day_of_week="*",
                      day_of_month="*", month_of_year="*"):
        schedule = self.api.make_schedule_dict({
            u'minute': minute,
            u'hour': hour,
            u'day_of_week': day_of_week,
            u'day_of_month': day_of_month,
            u'month_of_year': month_of_year,
            u'created_at': u'2014-07-25 12:44:11.159151',
            u'updated_at': u'2014-07-25 12:44:11.159151',
        })
        self.api.schedules.endpoint_data[schedule["id"]] = schedule
        return Struct(**schedule)

    def get_schedule(self, schedule_id=None):
        data = self.api.schedules.endpoint_data
        if schedule_id is None:
            return data.popitem()[1]
        else:
            return data.get(schedule_id)

    def get_schedules(self):
        data = self.api.schedules.endpoint_data
        s = []
        for key, schedule in data.iteritems():
            s.append(schedule)
        return s

    def make_messageset(self, default_schedule, short_name="new set",
                        next_set=None):
        messageset = self.api.make_messageset_dict({
            u'short_name': short_name,
            u'next_set': next_set,
            u'default_schedule': default_schedule,
        })
        self.api.messagesets.endpoint_data[messageset["id"]] = messageset
        return Struct(**messageset)

    def get_messageset(self, messageset_id=None):
        data = self.api.messagesets.endpoint_data
        if messageset_id is None:
            return data.popitem()[1]
        else:
            return data.get(messageset_id)

    def get_messagesets(self):
        return self.api.messagesets.endpoint_data.values()

    def make_message(self, messageset, sequence_number=1, lang="eng_GB",
                     text_content="Testing 1 2 3", binary_content=None):
        message = self.api.make_message_dict({
            u'messageset': messageset.id,
            u'sequence_number': sequence_number,
            u'lang': lang,
            u'text_content': text_content,
            u'binary_content': binary_content,
        })
        self.api.messages.endpoint_data[message["id"]] = message
        return Struct(**message)

    def get_message(self, message_id=None):
        data = self.api.messages.endpoint_data
        if message_id is None:
            return data.popitem()[1]
        else:
            return data.get(message_id)

    def get_messages(self):
        return self.api.messages.endpoint_data.values()


class TestContentStoreBinary(TestCase, ContentStoreBinaryApiTestMixin):

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

    def get_schedules(self):
        d = Schedule.objects.all()
        s = []
        for schedule in d:
            s.append(ScheduleSerializer(schedule).data)
        return s

    def make_messageset(self, default_schedule, short_name="new set",
                        next_set=None):
        message_set, created = MessageSet.objects.get_or_create(
            short_name=short_name, next_set=next_set,
            default_schedule_id=default_schedule)
        return message_set

    def get_messageset(self, messageset_id=None):
        if messageset_id is None:
            d = MessageSet.objects.last()
        else:
            d = MessageSet.objects.get(pk=messageset_id)
        return MessageSetSerializer(d).data

    def get_messagesets(self):
        d = MessageSet.objects.all()
        s = []
        for messageset in d:
            s.append(MessageSetSerializer(messageset).data)
        return s

    def make_message(self, messageset, sequence_number=1, lang="eng_GB",
                     text_content="Testing 1 2 3", binary_content=None):
        message, created = Message.objects.get_or_create(
            messageset_id=messageset, sequence_number=sequence_number,
            lang=lang, text_content=text_content,
            binary_content_id=binary_content)
        return message

    def get_message(self, message_id=None):
        if message_id is None:
            d = Message.objects.last()
        else:
            d = Message.objects.get(pk=message_id)
        return MessageSerializer(d).data

    def get_messages(self):
        d = Message.objects.all()
        s = []
        for message in d:
            s.append(MessageSerializer(message).data)
        return s

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

    def get_binary_content(self, binary_content_id=None):
        if binary_content_id is None:
            d = BinaryContent.objects.last()
        else:
            d = BinaryContent.objects.get(pk=binary_content_id)
        return BinaryContentSerializer(d).data

    def get_binary_contents(self):
        d = BinaryContent.objects.all()
        s = []
        for binary_content in d:
            s.append(BinaryContentSerializer(binary_content).data)
        return s
