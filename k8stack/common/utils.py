from contextlib import suppress
import logging
import subprocess
import sys
import os

from easy2use.system import OS

from k8stack.common import exceptions

LOG = logging.getLogger(__name__)


def run_popen(cmd: list):
    LOG.debug('Run: %s', ' '.join(cmd))
    popen = subprocess.Popen(cmd, stdout=sys.stdout)
    popen.wait()
    LOG.debug('Return: %s', popen.returncode)
    return popen.returncode


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
        status = run_popen(cmd)
        if status != 0:
            raise RuntimeError(f'docker build return {status}')

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
            raise RuntimeError(f'docker push return {status}')

    @classmethod
    def image_ls(cls, all=False):
        cmd = [cls.cmd, 'image', 'ls']
        if all:
            cmd.append('--all')
        status, output = subprocess.getstatusoutput(' '.join(cmd))
        if status != 0:
            raise RuntimeError('list image failed')
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
