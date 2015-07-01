
"""
Client for Messaging Content Store HTTP services APIs.

"""
import requests
import json


class ContentStoreApiClient(object):

    """
    Client for Content Store API.

    :param str auth_token:

        An access token.

    :param str api_url:
        The full URL of the API. Defaults to
        ``http://testserver/contentstore``.

    """

    def __init__(self, auth_token, api_url=None, session=None):
        self.auth_token = auth_token
        if api_url is None:
            api_url = "http://testserver/contentstore"
        self.api_url = api_url
        self.headers = {
            'Authorization': 'Token ' + auth_token,
            'Content-Type': 'application/json'
        }
        if session is None:
            session = requests.Session()
        session.headers.update(self.headers)
        self.session = session

    def call(self, endpoint, method, obj=None, params=None, data=None):
        if obj is None:
            url = '%s/%s' % (self.api_url.rstrip('/'), endpoint)
        else:
            url = '%s/%s/%s' % (self.api_url.rstrip('/'), endpoint, obj)
        result = {
            'get': self.session.get,
            'post': self.session.post,
            'put': self.session.post,
            'delete': self.session.delete,
        }.get(method, None)(url, params=params, data=json.dumps(data))
        result.raise_for_status()
        return result.json()

    def get_messagesets(self, params=None):
        return self.call('messageset', 'get', params=params)

    def get_messageset(self, messageset_id):
        return self.call('messageset', 'get', obj=messageset_id)

    def get_messageset_messages(self, messageset_id):
        return self.call('messageset', 'get',
                         obj='%s/messages' % messageset_id)

    def create_messageset(self, messageset):
        return self.call('messageset', 'post', data=messageset)

    def update_messageset(self, messageset_id, messageset):
        return self.call('messageset', 'put', obj=messageset_id,
                         data=messageset)

    def delete_messageset(self, messageset_id):
        return self.call('messageset', 'delete', obj=messageset_id)

    def get_messages(self, params=None):
        return self.call('message', 'get', params=params)

    def get_message(self, message_id):
        return self.call('message', 'get', obj=message_id)

    def get_message_content(self, message_id):
        return self.call('message', 'get',
                         obj='%s/content' % message_id)

    def create_message(self, message):
        return self.call('message', 'post', data=message)

    def update_message(self, message_id, message):
        return self.call('message', 'put', obj=message_id,
                         data=message)

    def delete_message(self, message_id):
        return self.call('message', 'delete', obj=message_id)

    def get_schedules(self, params=None):
        return self.call('schedule', 'get', params=params)

    def get_schedule(self, schedule_id):
        return self.call('schedule', 'get', obj=schedule_id)

    def create_schedule(self, schedule):
        return self.call('schedule', 'post', data=schedule)

    def update_schedule(self, schedule_id, schedule):
        return self.call('schedule', 'put', obj=schedule_id,
                         data=schedule)

    def delete_schedule(self, schedule_id):
        return self.call('schedule', 'delete', obj=schedule_id)

    def get_binarycontents(self, params=None):
        return self.call('binarycontent', 'get', params=params)

    def get_binarycontent(self, binarycontent_id):
        return self.call('binarycontent', 'get', obj=binarycontent_id)

    def create_binarycontent(self, binarycontent):
        post_data = {
            "content": binarycontent
        }
        url = '%s/binarycontent/' % (self.api_url.rstrip('/'),)
        result = self.session.post(url, data=post_data,
                                   format='multipart')
        result.raise_for_status()
        return result.json()

    def update_binarycontent(self, binarycontent_id, binarycontent):
        post_data = {
            "content": binarycontent
        }
        url = '%s/binarycontent/%s/' % (self.api_url.rstrip('/'),
                                        binarycontent_id)
        result = self.session.put(url, data=post_data,
                                  format='multipart')
        result.raise_for_status()
        return result.json()

    def delete_binarycontent(self, binarycontent_id):
        return self.call('binarycontent', 'delete', obj=binarycontent_id)
