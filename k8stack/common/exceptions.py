from easy2use.common.exceptions import BaseException


class DockerPushFailed(BaseException):
    _msg = 'Push {image} failed, {error}'
