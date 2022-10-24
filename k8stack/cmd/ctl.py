from genericpath import isfile
import glob
import logging
import os
import re
import shutil
import sys
import tempfile

import prettytable

from easy2use.globals import cli

from k8stack.common.i18n import _
from k8stack.common import conf
from k8stack.common import exceptions
from k8stack.common import registry_api
from k8stack.common import utils

LOG = logging.getLogger(__name__)
CONF = conf.CONF
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG_ARGS = cli.ArgGroup(
    'log arguments',
    [cli.Arg('-d', '--debug', action='store_true', help='Show debug message')]
)


class ComponentList(cli.SubCli):
    NAME = 'component-list'
    HELP = 'List components'
    ARGUMENTS = [LOG_ARGS]

    def __call__(self, args):
        conf.load_configs()
        LOG.debug('data path: %s', CONF.data_path)
        components_path = os.path.join(CONF.data_path, 'components')

        os.chdir(components_path)
        table = prettytable.PrettyTable(['No.', 'Name'])
        for i, c_path in enumerate(glob.glob(f'**/{CONF.dockerfile}',
                                             recursive=True)):
            path_list = c_path.split(os.sep)[:-1]
            table.add_row([str(i+1), os.sep.join(path_list)])
        table.align["Name"] = 'l'
        print(table)


class ImageList(cli.SubCli):
    NAME = 'image-list'
    HELP = 'List images'
    ARGUMENTS = [LOG_ARGS] + [
        cli.Arg('-o', '--only', action='store_true',
                help='Filter by taget registry'),
        cli.Arg('-r', '--registry', action='store_true',
                help='List images from registry'),
    ]

    def list_from_registry(self):
        pt = prettytable.PrettyTable(['Image', 'Tags'])
        for endpoint in CONF.push_registries:
            client = registry_api.ClientV2(endpoint)
            for image in client.image_ls() or []:
                if not image.startswith(f'{CONF.project}/'):
                    continue
                tags = client.tags(image)
                pt.align['Image'] = 'l'
                pt.align['Tags'] = 'l'
                pt.add_row([image, '    '.join(tags)])
        print(pt)

    def __call__(self, args):
        conf.load_configs()
        if args.registry:
            self.list_from_registry()
            return

        output_lines = utils.DockerCmd.image_ls().split('\n')
        for line in output_lines[1:]:
            if args.only and not line.startswith(f'{CONF.project}/'):
                continue
            print(line)


class Build(cli.SubCli):
    NAME = 'build'
    HELP = 'build container image'
    ARGUMENTS = [LOG_ARGS] + [
        cli.Arg('component', help='Component to build, get by `list` command'),
        cli.Arg('-n', '--no-cache', action='store_true',
                help='Build with no cache'),
        cli.Arg('-p', '--push',action='store_true', help='Push image'),
        cli.Arg('-v', '--version', help='Build version'),
    ]

    def parse_hosts_mapping(self):

        def _parse_to_arg(host, ip):
            host_arg = re.sub(r'\.|-', '_', host).upper()
            return f'{host_arg}={ip}'

        return [_parse_to_arg(k, v) for k, v in CONF.hosts_mapping.items()]

    def _prepare(self, component, dest_path):
        components_path = os.path.join(CONF.data_path, 'components')
        resources_path = os.path.join(CONF.data_path, 'resources',
                                      CONF.dockerfile)
        component_path = os.path.join(components_path, component)
        for src_path in glob.glob(os.path.join(component_path, '*')):
            shutil.copy(src_path, dest_path)

        if not os.path.exists(resources_path):
            LOG.warning('resources path %s is not exists', resources_path)
            return
        for src_path in glob.glob(os.path.join(resources_path, '*')):
            shutil.copy(src_path, dest_path)

    def __call__(self, args):
        conf.load_configs()
        LOG.debug('data path: %s', CONF.data_path)

        build_args = CONF.build_args
        build_args.extend(self.parse_hosts_mapping())
        version = args.version or CONF.build_version
        build_args.append(f'VERSION={version}')

        target = f'{CONF.project}/{args.component}:{version}'
        with tempfile.TemporaryDirectory() as build_context:
            self._prepare(args.component, build_context)
            LOG.info('Building ...')
            utils.DockerCmd.build(
                path=build_context,
                dockerfile=os.path.join(build_context, CONF.dockerfile),
                network=CONF.build_network,
                build_args=build_args,
                no_cache=args.no_cache,
                target=target,
            )
        for registry in CONF.push_registries:
            new_tag = f'{registry}/{target}'
            utils.DockerCmd.tag(target, new_tag)
            if args.push:
                LOG.info('Pushing %s ...', new_tag)
                try:
                    utils.DockerCmd.push(new_tag)
                except exceptions.DockerPushFailed as e:
                    LOG.error(e)


def main():
    cli_parser = cli.SubCliParser(_('K8Stack Command Line'),
                                  title=_('Subcommands'))
    cli_parser.register_clis(ComponentList, ImageList, Build)
    cli_parser.call()


if __name__ == '__main__':
    sys.exit(main())