"""
A verified fake implementation of django-messaging-contentstore for use
in tests.

This implementation is tested in the django-messaging-contentstore package
alongside the API it is faking, to ensure that the behaviour is the
same for both.
"""


import json
import weakref
from urlparse import urlparse, parse_qs
from random import randint


class Request(object):

    """
    Representation of an HTTP request.
    """

    def __init__(self, method, path, body=None, headers=None):
        self.method = method
        self.path = path
        self.body = body
        self.headers = headers if headers is not None else {}


class Response(object):

    """
    Representation of an HTTP response.
    """

    def __init__(self, code, headers, data):
        self.code = code
        self.headers = headers if headers is not None else {}
        self.data = data
        self.body = json.dumps(data)


class FakeObjectError(Exception):

    """
    Error we can use to craft a different HTTP response.
    """

    def __init__(self, code, reason):
        super(FakeObjectError, self).__init__()
        self.code = code
        self.reason = reason
        self.data = reason


def _data_to_json(data):
    if not isinstance(data, basestring):
        # If we don't already have JSON, we want to make some to guarantee
        # encoding succeeds.
        data = json.dumps(data)
    return json.loads(data)


class FakeEndpoint(object):

    """
    FakeEndpoint base class
    """

    def __init__(self, parent, endpoint_data={}):
        self.parent = weakref.ref(parent)
        self.endpoint_data = endpoint_data
        self.required_fields = None
        self.unique_fields = None

    @staticmethod
    def make_dict(fields):
        data = {
            u'id': randint(1, 100000000),
            u'created_at': u'2014-07-25 12:44:11.159151',
            u'updated_at': u'2014-07-25 12:44:11.159151',
        }
        data.update(fields)
        return data

    def _check_fields(self, fieldset):
        allowed_fields = set(self.make_dict({}).keys())
        allowed_fields.discard(u"id")

        bad_fields = set(fieldset.keys()) - allowed_fields
        if bad_fields:
            raise FakeObjectError(
                400, "Invalid fields: %s" % ", ".join(
                    sorted(bad_fields)))

    def _check_fields_required(self, fieldset):
        for field in self.required_fields:
            try:
                if fieldset[field] is None:
                    raise FakeObjectError(
                        400, "{'%s': ['This field is required.']}" % field)
            except KeyError:
                raise FakeObjectError(
                    400, "{'%s': ['This field is required.']}" % field)

    def _check_fields_unique(self, datastore):
        unique_fields = self.unique_fields

        for field in unique_fields:
            uniques = len(set(v[field] for (k, v) in datastore.items()))
            allvals = len(list(v[field] for (k, v) in datastore.items()))
            if (uniques - allvals) != 0:
                raise FakeObjectError(
                    400, "{'%s': ['This field must be unique.']}" % field)

    def create_object(self, endpoint_data):
        endpoint_data = _data_to_json(endpoint_data)
        self._check_fields(endpoint_data)
        self._check_fields_required(endpoint_data)

        newobject = self.make_dict(endpoint_data)
        self.endpoint_data[newobject[u"id"]] = newobject
        self._check_fields_unique(self.endpoint_data)
        return newobject

    def get_object(self, object_key, sub_request=None):
        existingobject = self.endpoint_data.get(object_key)
        if existingobject is None:
            raise FakeObjectError(
                404, u"Object %r not found." % (object_key,))
        return existingobject

    def get_all_objects(self, query):
        if query is not None:
            raise FakeObjectError(400, "query parameter not supported")
        return self.endpoint_data.values()

    def get_all(self, query):
        q = query.get('query', None)
        q = q and q[0]
        return self.get_all_objects(q)

    def update_object(self, object_key, endpoint_data):
        existingobject = self.get_object(object_key)
        endpoint_data = _data_to_json(endpoint_data)
        self._check_fields(endpoint_data)
        for k, v in endpoint_data.iteritems():
            existingobject[k] = v
        self.endpoint_data[object_key] = existingobject
        self._check_fields_required(existingobject)  # After to allow PATCH
        self._check_fields_unique(self.endpoint_data)
        return existingobject

    def delete_object(self, object_key):
        existingobject = self.get_object(object_key)
        self.endpoint_data.pop(object_key)
        return existingobject

    def request(self, request, object_key, query, sub_request):
        if request.method == "POST":
            if object_key is None or object_key is "":
                if request.headers["Content-Type"] == "application/json":
                    return (201, self.create_object(request.body))
                else:
                    # TODO Support 'multipart/form-data'
                    return FakeObjectError(405, "")
            else:
                raise FakeObjectError(405, "")
        if request.method == "GET":
            if object_key is None or object_key is "":
                return (200, self.get_all(query))
            else:
                return (200, self.get_object(object_key, sub_request))
        elif request.method == "PUT":
            # NOTE: This is an incorrect use of the PUT method, but
            # it's what we have for now.
            return (200, self.update_object(object_key, request.body))
        elif request.method == "PATCH":
            return (200, self.update_object(object_key, request.body))
        elif request.method == "DELETE":
            return (204, self.delete_object(object_key))
        else:
            raise FakeObjectError(405, "")


class FakeMessageSet(FakeEndpoint):

    def __init__(self, parent, endpoint_data={}):
        super(FakeMessageSet, self).__init__(parent, endpoint_data)
        self.required_fields = [u"short_name", u"default_schedule"]
        self.unique_fields = [u"short_name"]

    @staticmethod
    def make_dict(fields):
        data = {
            u'id': randint(1, 100000000),
            u'short_name': None,
            u'notes': None,
            u'next_set': None,
            u'default_schedule': None,
            u'created_at': u'2014-07-25 12:44:11.159151',
            u'updated_at': u'2014-07-25 12:44:11.159151',
        }
        data.update(fields)
        return data

    def get_object(self, object_key, sub_request=None):
        # Override to support messageset messages
        existingobject = self.endpoint_data.get(object_key)
        if existingobject is None:
            raise FakeObjectError(
                404, u"Object %r not found." % (object_key,))
        if sub_request is not None:
            # get messages - assumes all messages in fake are for current set
            messages = sorted(self.parent().messages.endpoint_data.values(),
                              key=lambda k: k['sequence_number'])
            existingobject["messages"] = messages
        return existingobject


class FakeSchedule(FakeEndpoint):

    def __init__(self, parent, endpoint_data={}):
        super(FakeSchedule, self).__init__(parent, endpoint_data)
        self.required_fields = [u"minute", u"hour", u"day_of_week",
                                u"day_of_month", u"month_of_year"]
        self.unique_fields = []

    @staticmethod
    def make_dict(fields):
        data = {
            u'id': randint(1, 100000000),
            u'minute': "*",
            u'hour': "*",
            u'day_of_week': "*",
            u'day_of_month': "*",
            u'month_of_year': "*",
            u'created_at': u'2014-07-25 12:44:11.159151',
            u'updated_at': u'2014-07-25 12:44:11.159151',
        }
        data.update(fields)
        return data


class FakeMessage(FakeEndpoint):

    def __init__(self, parent, endpoint_data={}):
        super(FakeMessage, self).__init__(parent, endpoint_data)
        self.required_fields = [u"messageset", u"sequence_number",
                                u"lang"]
        self.unique_fields = []

    @staticmethod
    def make_dict(fields):
        data = {
            u'id': randint(1, 100000000),
            u'messageset': None,
            u'sequence_number': None,
            u'lang': None,
            u'text_content': None,
            u'binary_content': None,
            u'created_at': u'2014-07-25 12:44:11.159151',
            u'updated_at': u'2014-07-25 12:44:11.159151',
        }
        data.update(fields)
        return data


class FakeBinaryContent(FakeEndpoint):

    def __init__(self, parent, endpoint_data={}):
        super(FakeBinaryContent, self).__init__(parent, endpoint_data)
        self.required_fields = [u"content"]
        self.unique_fields = []

    @staticmethod
    def make_dict(fields):
        data = {
            u'id': randint(1, 100000000),
            u'content': None,
            u'created_at': u'2014-07-25 12:44:11.159151',
            u'updated_at': u'2014-07-25 12:44:11.159151',
        }
        data.update(fields)
        return data


class FakeContentStoreApi(object):

    """
    Fake implementation of the content store API.
    """

    def __init__(self, url_path_prefix, auth_token, messageset_data={},
                 schedule_data={}, message_data={}, binary_content_data={}):
        self.url_path_prefix = url_path_prefix
        self.auth_token = auth_token
        self.messagesets = FakeMessageSet(self, messageset_data)
        self.schedules = FakeSchedule(self, schedule_data)
        self.messages = FakeMessage(self, message_data)
        self.binary_contents = FakeBinaryContent(self, binary_content_data)

    make_messageset_dict = staticmethod(FakeMessageSet.make_dict)
    make_schedule_dict = staticmethod(FakeSchedule.make_dict)
    make_message_dict = staticmethod(FakeMessage.make_dict)
    make_binary_content_dict = staticmethod(FakeBinaryContent.make_dict)

    # The methods below are part of the external API.

    def handle_request(self, request):
        if not self.check_auth(request):
            return self.build_response("", 403)
        url = urlparse(request.path)
        request.path = url.path.strip("/").replace(self.url_path_prefix, '')
        parts = request.path.split("/")
        request_type, key, sub_request = None, None, None
        if len(parts) >= 1:
            request_type = parts[0]
        if len(parts) >= 2:
            key = parts[1]
        if len(parts) >= 3:
            sub_request = parts[2]

        try:
            key = int(key)
        except (ValueError, TypeError) as err:
            pass  # not a pk

        handler = {
            'messageset': self.messagesets,
            'schedule': self.schedules,
            'message': self.messages,
            'binarycontent': self.binary_contents,
        }.get(request_type, None)

        if handler is None:
            self.build_response("", 404)

        try:
            query_string = parse_qs(url.query.decode('utf8'))
            result = handler.request(request, key, query_string, sub_request)
            return self.build_response(result[1], code=result[0],
                                       headers=request.headers)
        except FakeObjectError as err:
            return self.build_response(err.data, err.code)

    def check_auth(self, request):
        auth_header = request.headers.get("Authorization")
        return auth_header == "Token %s" % (self.auth_token,)

    def build_response(self, content, code=200, headers=None):
        return Response(code, headers, content)
