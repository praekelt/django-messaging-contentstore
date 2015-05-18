
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

    def get_messagesets(self, params=None):
        url = '%s/messageset/' % (self.api_url.rstrip('/'),)
        result = self.session.get(url, params=params)
        result.raise_for_status()
        return result.json()

    def get_messageset(self, messageset_id):
        url = '%s/messageset/%s/' % (self.api_url.rstrip('/'), messageset_id)
        result = self.session.get(url)
        result.raise_for_status()
        return result.json()

    def get_messageset_messages(self, messageset_id):
        url = '%s/messageset/%s/messages' % (self.api_url.rstrip('/'),
                                             messageset_id)
        result = self.session.get(url)
        result.raise_for_status()
        return result.json()

    def create_messageset(self, messageset):
        url = '%s/messageset/' % (self.api_url.rstrip('/'),)
        result = self.session.post(url, data=json.dumps(messageset))
        result.raise_for_status()
        return result.json()

    def update_messageset(self, messageset_id, messageset):
        url = '%s/messageset/%s/' % (self.api_url.rstrip('/'), messageset_id)
        result = self.session.put(url, data=json.dumps(messageset))
        result.raise_for_status()
        return result.json()

    def delete_messageset(self, messageset_id):
        url = '%s/messageset/%s/' % (self.api_url.rstrip('/'), messageset_id)
        result = self.session.delete(url)
        result.raise_for_status()
        return result.json()

    def get_messages(self, params=None):
        url = '%s/message/' % (self.api_url.rstrip('/'),)
        result = self.session.get(url, params=params)
        result.raise_for_status()
        return result.json()

    def get_message(self, message_id):
        url = '%s/message/%s/' % (self.api_url.rstrip('/'), message_id)
        result = self.session.get(url)
        result.raise_for_status()
        return result.json()

    def get_message_content(self, message_id):
        url = '%s/message/%s/content' % (self.api_url.rstrip('/'), message_id)
        result = self.session.get(url)
        result.raise_for_status()
        return result.json()

    def create_message(self, message):
        url = '%s/message/' % (self.api_url.rstrip('/'),)
        result = self.session.post(url, data=json.dumps(message))
        result.raise_for_status()
        return result.json()

    def update_message(self, message_id, message):
        url = '%s/message/%s/' % (self.api_url.rstrip('/'), message_id)
        result = self.session.put(url, data=json.dumps(message))
        result.raise_for_status()
        return result.json()

    def delete_message(self, message_id):
        url = '%s/message/%s/' % (self.api_url.rstrip('/'), message_id)
        result = self.session.delete(url)
        result.raise_for_status()
        return result.json()

    def get_schedules(self, params=None):
        url = '%s/schedule/' % (self.api_url.rstrip('/'),)
        result = self.session.get(url, params=params)
        result.raise_for_status()
        return result.json()

    def get_schedule(self, schedule_id):
        url = '%s/schedule/%s/' % (self.api_url.rstrip('/'), schedule_id)
        result = self.session.get(url)
        result.raise_for_status()
        return result.json()

    def create_schedule(self, schedule):
        url = '%s/schedule/' % (self.api_url.rstrip('/'),)
        result = self.session.post(url, data=json.dumps(schedule))
        result.raise_for_status()
        return result.json()

    def update_schedule(self, schedule_id, schedule):
        url = '%s/schedule/%s/' % (self.api_url.rstrip('/'), schedule_id)
        result = self.session.put(url, data=json.dumps(schedule))
        result.raise_for_status()
        return result.json()

    def delete_schedule(self, schedule_id):
        url = '%s/schedule/%s/' % (self.api_url.rstrip('/'), schedule_id)
        result = self.session.delete(url)
        result.raise_for_status()
        return result.json()

    def get_binarycontents(self, params=None):
        url = '%s/binarycontent/' % (self.api_url.rstrip('/'),)
        result = self.session.get(url, params=params)
        result.raise_for_status()
        return result.json()

    def get_binarycontent(self, binarycontent_id):
        url = '%s/binarycontent/%s/' % (self.api_url.rstrip('/'),
                                        binarycontent_id)
        result = self.session.get(url)
        result.raise_for_status()
        return result.json()

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
        url = '%s/binarycontent/%s/' % (self.api_url.rstrip('/'),
                                        binarycontent_id)
        result = self.session.delete(url)
        result.raise_for_status()
        return result.json()
