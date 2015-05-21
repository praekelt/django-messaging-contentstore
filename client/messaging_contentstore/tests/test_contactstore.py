"""
Tests for messaging_contentstore.contentstore.
"""

from unittest import TestCase

from requests import HTTPError
from requests.adapters import HTTPAdapter
from requests_testadapter import TestSession, Resp, TestAdapter

from verified_fake.fake_contentstore import Request, FakeContentStoreApi

from messaging_contentstore.contentstore import ContentStoreApiClient


class FakeContentStoreApiAdapter(HTTPAdapter):

    """
    Adapter for FakeContentStoreApi

    This inherits directly from HTTPAdapter instead of using TestAdapter
    because it overrides everything TestAdaptor does.
    """

    def __init__(self, contentstore_api):
        self.contentstore_api = contentstore_api
        super(FakeContentStoreApiAdapter, self).__init__()

    def send(self, request, stream=False, timeout=None,
             verify=True, cert=None, proxies=None):
        # print request.path_url
        req = Request(
            request.method, request.path_url, request.body, request.headers)
        resp = self.contentstore_api.handle_request(req)
        response = Resp(resp.body, resp.code, resp.headers)
        r = self.build_response(request, response)
        # print r.status_code
        return r


make_messageset_dict = FakeContentStoreApi.make_messageset_dict
make_message_dict = FakeContentStoreApi.make_message_dict
make_schedule_dict = FakeContentStoreApi.make_schedule_dict


class TestContentStoreApiClient(TestCase):
    API_URL = "http://example.com/contentstore"
    AUTH_TOKEN = "auth_token"

    def setUp(self):
        self.messageset_data = {}
        self.schedule_data = {}
        self.message_data = {}
        self.binary_content_data = {}
        self.contentstore_backend = FakeContentStoreApi(
            "contentstore/", self.AUTH_TOKEN,
            messageset_data=self.messageset_data,
            schedule_data=self.schedule_data, message_data=self.message_data,
            binary_content_data=self.binary_content_data)
        self.session = TestSession()
        adapter = FakeContentStoreApiAdapter(self.contentstore_backend)
        self.session.mount(self.API_URL, adapter)

    def make_client(self, auth_token=AUTH_TOKEN):
        return ContentStoreApiClient(
            auth_token, api_url=self.API_URL, session=self.session)

    def make_existing_messageset(self, messageset_data):
        existing_messageset = make_messageset_dict(messageset_data)
        self.contentstore_backend.messagesets.endpoint_data[
            existing_messageset[u"id"]] = existing_messageset
        return existing_messageset

    def make_existing_message(self, message_data):
        existing_message = make_message_dict(message_data)
        self.contentstore_backend.messages.endpoint_data[
            existing_message[u"id"]] = existing_message
        return existing_message

    def make_existing_schedule(self, schedule_data):
        existing_schedule = make_schedule_dict(schedule_data)
        self.contentstore_backend.schedules.endpoint_data[
            existing_schedule[u"id"]] = existing_schedule
        return existing_schedule

    def assert_messageset_status(self, messageset_id, exists=True):
        exists_status = (messageset_id in self.messageset_data)
        self.assertEqual(exists_status, exists)

    def assert_http_error(self, expected_status, func, *args, **kw):
        try:
            func(*args, **kw)
        except HTTPError as err:
            self.assertEqual(err.response.status_code, expected_status)
        else:
            self.fail(
                "Expected HTTPError with status %s." % (expected_status,))

    def test_assert_http_error(self):
        self.session.mount("http://bad.example.com/", TestAdapter("", 500))

        def bad_req():
            r = self.session.get("http://bad.example.com/")
            r.raise_for_status()

        # Fails when no exception is raised.
        self.assertRaises(
            self.failureException, self.assert_http_error, 404, lambda: None)

        # Fails when an HTTPError with the wrong status code is raised.
        self.assertRaises(
            self.failureException, self.assert_http_error, 404, bad_req)

        # Passes when an HTTPError with the expected status code is raised.
        self.assert_http_error(500, bad_req)

        # Non-HTTPError exceptions aren't caught.
        def raise_error():
            raise ValueError()

        self.assertRaises(ValueError, self.assert_http_error, 404, raise_error)

    def test_default_session(self):
        import requests
        contentstore = ContentStoreApiClient(self.AUTH_TOKEN)
        self.assertTrue(isinstance(contentstore.session, requests.Session))

    def test_default_api_url(self):
        contentstore = ContentStoreApiClient(self.AUTH_TOKEN)
        self.assertEqual(
            contentstore.api_url, "http://testserver/contentstore")

    def test_auth_failure(self):
        contentstore = self.make_client(auth_token="bogus_token")
        self.assert_http_error(403, contentstore.get_messagesets)

    def test_get_messageset(self):
        expected_messageset = self.make_existing_messageset({
            u"short_name": u"Full Set",
            u"notes": u"A full set of messages.",
            u"default_schedule": 1
        })
        contentstore = self.make_client()
        [messageset] = list(contentstore.get_messagesets())
        self.assertEqual(messageset, expected_messageset)

    def test_create_messageset(self):
        contentstore = self.make_client()
        new_messageset = contentstore.create_messageset({
            u"short_name": u"Full Set1",
            u"notes": u"A full and new set of messages.",
            u"default_schedule": 1
        })
        [messageset] = list(contentstore.get_messagesets())
        self.assertEqual(
            messageset["short_name"], new_messageset["short_name"])
        self.assertEqual(
            messageset["notes"], new_messageset["notes"])
        self.assertEqual(
            messageset["default_schedule"], new_messageset["default_schedule"])

    def test_get_message(self):
        expected_message = self.make_existing_message({
            "messageset": 1,
            "sequence_number": 2,
            "lang": "afr_ZA",
            "text_content": "Message two"
        })
        contentstore = self.make_client()
        [message] = list(contentstore.get_messages())
        self.assertEqual(message, expected_message)

    def test_create_message(self):
        contentstore = self.make_client()
        new_message = contentstore.create_message({
            "messageset": 1,
            "sequence_number": 2,
            "lang": "afr_ZA",
            "text_content": "Message two"
        })
        [message] = list(contentstore.get_messages())
        self.assertEqual(message["text_content"],
                         new_message["text_content"])
        self.assertEqual(message["sequence_number"],
                         new_message["sequence_number"])
        self.assertEqual(message["messageset"],
                         new_message["messageset"])
        self.assertEqual(message["lang"],
                         new_message["lang"])

    def test_get_schedule(self):
        expected_schedule = self.make_existing_schedule({
            "minute": "1",
            "hour": "2",
            "day_of_week": "3",
            "day_of_month": "4",
            "month_of_year": "5",
        })
        contentstore = self.make_client()
        [schedule] = list(contentstore.get_schedules())
        self.assertEqual(schedule, expected_schedule)

    def test_create_schedule(self):
        contentstore = self.make_client()
        new_schedule = contentstore.create_schedule({
            "minute": "1",
            "hour": "2",
            "day_of_week": "3",
            "day_of_month": "4",
            "month_of_year": "5",
        })
        [schedule] = list(contentstore.get_schedules())
        self.assertEqual(schedule["minute"],
                         new_schedule["minute"])
        self.assertEqual(schedule["hour"],
                         new_schedule["hour"])
        self.assertEqual(schedule["day_of_week"],
                         new_schedule["day_of_week"])
        self.assertEqual(schedule["day_of_month"],
                         new_schedule["day_of_month"])
        self.assertEqual(schedule["month_of_year"],
                         new_schedule["month_of_year"])
