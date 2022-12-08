from k8stack.common import conf
from k8stack.common.container import impl

CONF = conf.CONF

global CONTAINER_CLI

CONTAINER_CLI = None


CONTAINER_CLI_MAP = {
    'docker': impl.DockerCmd,
    'podman': impl.PodmanCmd,
    'nerdctl': impl.NerdCtlCmd,
}


def init():
    global CONTAINER_CLI

    CONTAINER_CLI = CONTAINER_CLI_MAP.get(CONF.container_cli)
    if not CONTAINER_CLI:
        raise ValueError(f'Invalid container_clid {CONF.container_cli}')
