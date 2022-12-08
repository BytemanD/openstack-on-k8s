import requests


class ClientV2(object):
    """
    Docker Registry V2 Client
    """
    VERSION = 'v2'

    def __init__(self, registry, insecure=False):
        self.registry = registry
        self.session = requests.Session()
        self.insecure = insecure
        self.endpoint = self._make_endpoint()

    def _make_endpoint(self):
        schema = self.insecure and 'http' or 'https'
        return f'{schema}://{self.registry}/{self.VERSION}'

    def image_ls(self):
        resp = self.session.get(f'{self.endpoint}/_catalog', verify=False)
        return resp.json().get('repositories')

    def tags(self, image):
        resp = self.session.get(f'{self.endpoint}/{image}/tags/list')
        return resp.json().get('tags')
