import requests


class ClientV2(object):
    """
    Docker Registry V2 Client
    """
    VERSION = 'v2'

    def __init__(self, registry):
        self.registry = registry
        self.session = requests.Session()
        self.endpoint = f'http://{self.registry}/{self.VERSION}'

    def image_ls(self):
        resp = self.session.get(f'{self.endpoint}/_catalog')
        return resp.json().get('repositories')

    def tags(self, image):
        resp = self.session.get(f'{self.endpoint}/{image}/tags/list')
        return resp.json().get('tags')
