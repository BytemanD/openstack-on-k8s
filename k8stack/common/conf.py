import os
import logging

from easy2use.globals import cfg

LOG = logging.getLogger(__name__)

CONF = cfg.CONF

default_options = [
    cfg.BooleanOption('debug', default=False),
    cfg.Option('log_file', default=None),
    cfg.Option('data_path', default='data'),
    cfg.MapOption('hosts_mapping', default={}),

    cfg.Option('dockerfile', default='Dockerfile'),
    cfg.Option('build_network', default=None),
    cfg.Option('build_version', default='latest'),
    cfg.ListOption('build_args', default=[]),

    cfg.Option('project', default='k8stack'),
    cfg.ListOption('push_registries', default=[]),
    cfg.Option('deploy_registry', default=None),
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
