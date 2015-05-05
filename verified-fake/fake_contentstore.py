"""
A verified fake implementation of django-messaging-contentstore for use
in tests.

This implementation is tested in the django-messaging-contentstore package
alongside the API it is faking, to ensure that the behaviour is the
same for both.
"""


import json
from urlparse import urlparse, parse_qs
from random import randint


"""
Missing required - 400

{
    "field_name": [
        "This field is required."
    ]
}
Too long
{
    "short_name": [
        "Ensure this field has no more than 20 characters."
    ]
}

Unathorized - 401
{
    "detail": "Invalid token."
}

"""


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


class FakeMessageSetError(Exception):

    """
    Error we can use to craft a different HTTP response.
    """

    def __init__(self, code, reason):
        super(FakeMessageSetError, self).__init__()
        self.code = code
        self.reason = reason
        self.data = reason


def _data_to_json(data):
    if not isinstance(data, basestring):
        # If we don't already have JSON, we want to make some to guarantee
        # encoding succeeds.
        data = json.dumps(data)
    return json.loads(data)


class FakeMessageSet(object):

    """
    Fake implementation of the MessageSet API
    """

    def __init__(self, messageset_data={}):
        self.messageset_data = messageset_data

    @staticmethod
    def make_messageset_dict(fields):
        messageset = {
            u'id': randint(1, 100000000),
            u'short_name': None,
            u'notes': None,
            u'next_set': None,
            u'default_schedule': 1,
            u'created_at': u'2014-07-25 12:44:11.159151',
            u'updated_at': u'2014-07-25 12:44:11.159151',
        }
        messageset.update(fields)
        return messageset

    def _check_fields(self, messageset):
        allowed_fields = set(self.make_messageset_dict({}).keys())
        allowed_fields.discard(u"id")

        bad_fields = set(messageset.keys()) - allowed_fields
        if bad_fields:
            raise FakeMessageSetError(
                400, "Invalid messageset fields: %s" % ", ".join(
                    sorted(bad_fields)))

    def create_messageset(self, messageset_data):
        messageset_data = _data_to_json(messageset_data)
        self._check_fields(messageset_data)

        messageset = self.make_messageset_dict(messageset_data)
        self.messageset_data[messageset[u"id"]] = messageset
        return messageset

    def get_messageset(self, messageset_key):
        messageset = self.messageset_data.get(messageset_key)
        if messageset is None:
            raise FakeMessageSetError(
                404, u"MessageSet %r not found." % (messageset_key,))
        return messageset

    def get_all_messagesets(self, query):
        if query is not None:
            raise FakeMessageSetError(400, "query parameter not supported")
        return self.messageset_data.values()

    def get_all(self, query):
        q = query.get('query', None)
        q = q and q[0]
        return self.get_all_messagesets(q)

    def update_messageset(self, messageset_key, messageset_data):
        messageset = self.get_messageset(messageset_key)
        messageset_data = _data_to_json(messageset_data)
        self._check_fields(messageset_data)
        for k, v in messageset_data.iteritems():
            messageset[k] = v
        return messageset

    def delete_messageset(self, messageset_key):
        messageset = self.get_messageset(messageset_key)
        self.messagesets_data.pop(messageset_key)
        return messageset

    def request(self, request, messageset_key, query, messageset_store):
        if request.method == "POST":
            if messageset_key is None or messageset_key is "":
                return self.create_messageset(request.body)
            else:
                raise FakeMessageSetError(405, "")
        if request.method == "GET":
            if messageset_key is None or messageset_key is "":
                return self.get_all(query)
            else:
                return self.get_messageset(messageset_key)
        elif request.method == "PUT":
            # NOTE: This is an incorrect use of the PUT method, but
            # it's what we have for now.
            return self.update_messageset(messageset_key, request.body)
        elif request.method == "DELETE":
            return self.delete_messageset(messageset_key)
        else:
            raise FakeMessageSetError(405, "")


class FakeContentStoreApi(object):

    """
    Fake implementation of the content store API.
    """

    def __init__(self, url_path_prefix, auth_token, messageset_data={}):
        self.url_path_prefix = url_path_prefix
        self.auth_token = auth_token
        self.messagesets = FakeMessageSet(messageset_data)

    make_messageset_dict = staticmethod(FakeMessageSet.make_messageset_dict)

    # The methods below are part of the external API.

    def handle_request(self, request):
        if not self.check_auth(request):
            return self.build_response("", 403)

        url = urlparse(request.path)
        request.path = url.path
        request_type = request.path.replace(
            self.url_path_prefix, '').lstrip('/')
        print "Request type"
        print request_type
        request_type = request_type[:request_type.find('/')]
        print "Request type"
        print request_type
        prefix = "/".join([self.url_path_prefix.rstrip("/"), request_type])
        print "Prefix"
        print prefix
        messageset_key = request.path.replace(prefix, "").lstrip("/")
        print "MessageSet key"
        messageset_key

        handler = {
            'messageset': self.messagesets,
        }.get(request_type, None)

        if handler is None:
            self.build_response("", 404)

        try:
            query_string = parse_qs(url.query.decode('utf8'))
            return self.build_response(
                handler.request(
                    request, messageset_key, query_string, self.messagesets))
        except FakeMessageSetError as err:
            return self.build_response(err.data, err.code)

    def check_auth(self, request):
        auth_header = request.headers.get("Authorization")
        return auth_header == "Token %s" % (self.auth_token,)

    def build_response(self, content, code=200, headers=None):
        return Response(code, headers, content)
