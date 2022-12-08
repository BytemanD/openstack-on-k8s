import contextlib
import glob
import logging
import shutil
import string
import subprocess
import sys
import os
import tempfile

from easy2use.system import OS

from k8stack.common import conf
from k8stack.common import exceptions

LOG = logging.getLogger(__name__)
CONF = conf.CONF


def run_popen(cmd: list, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
    LOG.debug('>>: %s', ' '.join(cmd))
    popen = subprocess.Popen(cmd, stdout=stdout, stderr=stderr)
    popen.wait()
    LOG.debug('>> [%s]: ', popen.returncode)

    if popen.returncode != 0:
        # import pdb; pdb.set_trace()
        LOG.error('>> [stderr]: %s', ''.join(
            [line.decode() for line in popen.stderr.readlines()]))
    else:
        LOG.info('>> [stdout]: %s', ''.join(popen.stdout.readlines() or ['']))
    return popen.returncode


def execute(cmd, debug_output=True):
    LOG.debug('>>: %s', ' '.join(cmd))
    status, output = subprocess.getstatusoutput(' '.join(cmd))
    LOG.debug('>> [code]: %s [output]: \n%s', status,
              debug_output and output or '***')
    return status, output


class DockerCmd(object):
    cmd = 'docker'

    @classmethod
    def build(cls, dockerfile='Dockerfile', path='./',
              network=None, build_args=None, target=None, no_cache=False):
        cmd = [cls.cmd, 'build', '-f', dockerfile]
        if network:
            cmd.extend(['--network', network])
        if no_cache:
            cmd.append('--no-cache')
        if build_args:
            for arg in build_args:
                cmd.extend(['--build-arg', arg])
        if target:
            cmd.extend(['-t', target])
        cmd.append(path)
        status = run_popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
        if status != 0:
            raise exceptions.DockerBuildFailed(target=target,
                                               error=f'return code {status}')

    @classmethod
    def tag(cls, image, tag):
        status = run_popen([cls.cmd, 'tag', image, tag])
        if status != 0:
            raise RuntimeError(f'docker tag return {status}')

    @classmethod
    def push(cls, image):
        status = run_popen([cls.cmd, 'push', image])
        if status != 0:
            raise exceptions.DockerPushFailed(image=image,
                                              error=f'return code: {status}')

    @classmethod
    def image_ls(cls, all=False):
        cmd = [cls.cmd, 'image', 'ls']
        if all:
            cmd.append('--all')
        status, output = subprocess.getstatusoutput(' '.join(cmd))
        if status != 0:
            raise RuntimeError('list image failed')
        return output


class PodmanCmd(DockerCmd):
    cmd = 'podman'


class NerdCtlCmd(DockerCmd):
    cmd = 'nerdctl'


class KubectlCmd(object):
    cmd = 'kubectl'

    @classmethod
    def replace(cls, file, force=False):
        cmd = [cls.cmd, 'replace']
        if force:
            cmd.append('--force')
        cmd.extend(['-f', file])
        status, output = execute(cmd)
        if status != 0:
            raise RuntimeError(f'replace {file} failed, {output}')

    @classmethod
    def delete(cls, file, force=False):
        cmd = [cls.cmd, 'delete']
        if force:
            cmd.append('--force')
        cmd.extend(['-f', file])
        status, output = subprocess.getstatusoutput(' '.join(cmd))
        if status != 0:
            raise RuntimeError(
                f'delete by file "{file}" failed, stdout:\n{output}')

    @classmethod
    def create_configmap(cls, name, from_file=None, dry_run=False,
                         output=None):
        cmd = [cls.cmd, 'create', 'configmap', name]
        for file in from_file or []:
            LOG.debug('found file %s', file)
            file_name = os.path.basename(file)
            cmd.append(f'--from-file={file_name}={file}')
        if dry_run:
            cmd.append('--dry-run=client')
        if output:
            cmd.append(f'--output={output}')

        status, output = execute(cmd, debug_output=False)
        if status != 0:
            raise RuntimeError(
                f'create configmap "{name}" failed, stdout:\n{output}')
        return output


def get_hosts_mapping():
    """Get hosts mapping

    e.g.  host1: 1.1.1.1
          host2: 1.1.1.2
    """
    if OS.is_windows():
        hosts_file = os.path.join('c:\\', 'Windows', 'System32', 'drivers',
                                  'etc', 'hosts')
    else:
        hosts_file = os.path.join('/', 'etc', 'hosts')
    if not os.path.exists(hosts_file):
        LOG.warn('hosts file is not exists: %s', hosts_file)
    hosts_mapping = {}
    with open(hosts_file, 'r', encoding='utf8') as f:
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            ip_host = line.split()
            if len(ip_host) < 2:
                LOG.warning('Invalid host mapping %s', line)
            if ip_host[0] == '127.0.0.1':
                continue
            hosts_mapping[ip_host[1]] = ip_host[0]
    return hosts_mapping


def prepare(component, dest_path):
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


def push_to_registries(local_registry, version, latest=False):
    target = f'{local_registry}:{version}'
    for registry in CONF.push_registries:
        push_tags = [f'{registry}/{local_registry}:{version}']
        if latest:
            push_tags.append(f'{registry}/{local_registry}:latest')

        for new_tag in push_tags:
            DockerCmd.tag(target, new_tag)
            LOG.info('Pushing %s ...', new_tag)
            try:
                DockerCmd.push(new_tag)
            except exceptions.DockerPushFailed as e:
                LOG.error(e)


def get_deploy_yaml(component, version=None, replicas=None):
    deploy_file = os.path.join(CONF.data_path, 'deployments',
                               component, 'deployment.yaml')
    with open(deploy_file) as f:
        template = string.Template(f.read())
    params = {
        'REGISTRY': CONF.deploy_registry and f'{CONF.deploy_registry}/' or '',
        'PROJECT': CONF.project,
        'VERSION': version or CONF.build_version,
        'REPLICAS': replicas or CONF.replicas.get(component, 1),
    }
    LOG.debug('deployment template params: %s', params)
    return template.safe_substitute(params)


@contextlib.contextmanager
def make_temp_file(content):
    file_fd, file_path = tempfile.mkstemp()

    try:
        with os.fdopen(file_fd, 'w') as f:
            f.write(content)
        yield file_path
    finally:
        try:
            os.remove(file_path)
        except Exception as e:
            LOG.warning('delete file %s failed, %s', file_path, e)
