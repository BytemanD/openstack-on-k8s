import os
import socket
import logging

from easy2use.globals import cfg
from easy2use.common.customconfig import Item, IntItem, BoolItem

LOG = logging.getLogger(__name__)

CONF = cfg.CONF
DEFAULT_HOST = socket.gethostname()

default_options = [
    cfg.BooleanOption('debug', default=False),
    cfg.Option('log_file', default=None),
    cfg.Option('data_path', default='data'),
    cfg.MapOption('hosts_mapping', default={}),
    
    cfg.Option('dockerfile', default='Dockerfile'),
    cfg.Option('build_network', default=None),
    cfg.Option('build_version', default=None),
    cfg.Option('taget_registry', default='k8stack'),
    cfg.ListOption('build_args', default=[]),
]


def load_configs():
    for file in ['/etc/k8stack/k8stack.conf',
                 os.path.join('etc', 'k8stack.conf')]:
        if not os.path.exists(file):
            continue
        LOG.debug('Load config file from %s', file)
        CONF.load(file)
        break
    else:
        LOG.warning('config file not found')


CONF.register_opts(default_options)
