import glob
import logging
import os
import re
import sys

import prettytable

from easy2use.globals import cli

from k8stack.common.i18n import _
from k8stack.common import conf
from k8stack.common import registry_api
from k8stack.common import utils
from k8stack.common import container
from k8stack.common.container import impl


LOG = logging.getLogger(__name__)
CONF = conf.CONF
CONTAINER_CLI = container.CONTAINER_CLI

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

        components = sorted([
            comp for comp in glob.glob(f'**/{CONF.dockerfile}', recursive=True)
        ])
        for i, c_path in enumerate(components):
            path_list = c_path.split(os.sep)[:-1]
            table.add_row([str(i+1), os.sep.join(path_list)])
        table.align["Name"] = 'l'
        print(table)


class ImageList(cli.SubCli):
    NAME = 'image-list'
    HELP = 'List images'
    ARGUMENTS = [LOG_ARGS] + [
        cli.Arg('name', nargs='?', help='Filter images'),
        cli.Arg('-r', '--registry', action='store_true',
                help='List images from registry'),
    ]

    def list_from_registry(self, name=None):
        pt = prettytable.PrettyTable(['Image', 'Tags'])
        for endpoint in CONF.push_registries:
            client = registry_api.ClientV2(endpoint)
            for image in client.image_ls() or []:
                if name and name not in image:
                    continue
                tags = client.tags(image)
                pt.align['Image'] = 'l'
                pt.align['Tags'] = 'l'
                pt.add_row([image, '    '.join(tags)])
        print(pt)

    def __call__(self, args):
        conf.load_configs()
        if args.registry:
            self.list_from_registry(name=args.name)
            return
        CLI = impl.get_container_cli()
        output_lines = CLI.image_ls().split('\n')
        print(output_lines[0])
        for line in output_lines[1:]:
            if args.name and args.name not in line:
                continue
            print(line)


class Build(cli.SubCli):
    NAME = 'build'
    HELP = 'build container image'
    ARGUMENTS = [LOG_ARGS] + [
        cli.Arg('component', help='Component to build, get by `list` command'),
        cli.Arg('-p', '--push', action='store_true', help='Push image'),
        cli.Arg('-n', '--no-cache', action='store_true',
                help='Build with no cache'),
        cli.Arg('-l', '--latest', action='store_true', help='Set latest tag'),
        cli.Arg('-v', '--version', help='Build version'),
    ]

    def parse_hosts_mapping(self):

        def _parse_to_arg(host, ip):
            host_arg = re.sub(r'\.|-', '_', host).upper()
            return f'{host_arg}={ip}'

        return [_parse_to_arg(k, v) for k, v in CONF.hosts_mapping.items()]

    def __call__(self, args):
        conf.load_configs()
        LOG.debug('data path: %s', CONF.data_path)

        version = args.version or CONF.build_version
        build_args = CONF.build_args
        build_args.extend(self.parse_hosts_mapping())
        build_args.append(f'VERSION={version}')

        local_registry = f'{CONF.project}/{args.component}'
        target = f'{local_registry}:{version}'

        impl.build_image(args.component, target, no_cache=args.no_cache,
                         build_args=build_args)

        if args.latest:
            impl.tag(target, f'{local_registry}:latest')

        if args.push:
            impl.push_to_registries(local_registry, version,
                                     latest=args.latest)


class Replace(cli.SubCli):
    NAME = 'replace'
    HELP = 'replace deployed component'
    ARGUMENTS = [LOG_ARGS] + [
        cli.Arg('component', nargs='+',
                help='Component to deploy, get by `list` command'),
        cli.Arg('-f', '--force', action='store_true',
                help=''),
        cli.Arg('-v', '--version', help='Version to run'),
        cli.Arg('-r', '--replicas', type=int, help='Replicas to run'),
    ]

    def __call__(self, args):
        conf.load_configs()
        LOG.debug('data path: %s', CONF.data_path)
        for component in args.component:
            result = utils.get_deploy_yaml(component, version=args.version,
                                           replicas=args.replicas)

            with utils.make_temp_file(result) as f:
                LOG.info('Replacing %s ...', component)
                utils.KubectlCmd.replace(f, force=args.force)


class Delete(cli.SubCli):
    NAME = 'delete'
    HELP = 'delete deployed component'
    ARGUMENTS = [LOG_ARGS] + [
        cli.Arg('component', nargs='+',
                help='Component to deploy, get by `list` command'),
        cli.Arg('-f', '--force', action='store_true'),
    ]

    def __call__(self, args):
        conf.load_configs()
        LOG.debug('data path: %s', CONF.data_path)
        for component in args.component:
            result = utils.get_deploy_yaml(component)

            with utils.make_temp_file(result) as f:
                LOG.info('Delete %s ...', component)
                utils.KubectlCmd.delete(f, force=args.force)


class CreateOrUpdateCM(cli.SubCli):
    NAME = 'create-or-update-cm'
    HELP = 'Create or update configmap'
    ARGUMENTS = [LOG_ARGS]

    def __call__(self, args):
        conf.load_configs()
        LOG.debug('data path: %s', CONF.data_path)

        scripts_dir = os.path.join(CONF.data_path, 'scripts')
        result = utils.KubectlCmd.create_configmap(
            'k8stack-scripts', from_file=glob.glob(f'{scripts_dir}/*'),
            dry_run=True, output='yaml')

        with utils.make_temp_file(result) as f:
            LOG.info('Replace configmap %s', 'k8stack-scripts')
            utils.KubectlCmd.replace(f, force=True)


def main():
    cli_parser = cli.SubCliParser(_('K8Stack Command Line'),
                                  title=_('Subcommands'))
    cli_parser.register_clis(ComponentList, ImageList, Build, Replace, Delete,
                             CreateOrUpdateCM)
    cli_parser.call()


if __name__ == '__main__':
    sys.exit(main())
