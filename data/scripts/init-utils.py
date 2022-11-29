import os
import sys
import logging
import argparse
import shutil
try:
    import commands as subprocess
except ImportError:
    import subprocess


FORMAT = '%(asctime)s %(process)d %(levelname)s %(name)s:%(lineno)s ' \
         '%(message)s'

LOG = logging.getLogger()

WORKSPACE = os.path.dirname(os.path.abspath(__file__))


def execute(cmd):
    LOG.debug('>> %s', ' '.join(cmd))
    status, output = subprocess.getstatusoutput(' '.join(cmd))
    LOG.debug('>> [%s]: %s', status, output)
    return status, output


def groupadd(group, gid=None):
    LOG.info('add group: %s', group)
    cmd = ['groupadd', '-r', group]
    if gid:
        cmd.extend(['--gid', str(gid)])
    status, output = execute(cmd)
    if status != 0 and 'already exists' not in output:
        raise RuntimeError('add group failed, {}'.format(output))


def useradd(user, uid=None, gid=None, groups=None, home_dir=None,
            bash=None, comment=None):
    LOG.info('add user: %s', user)
    cmd = ['useradd', '-r']
    if uid:
        cmd.extend(['-u', str(uid)])
    if gid:
        cmd.extend(['-g', str(gid)])
    if groups:
        cmd.extend(['-G', ','.join(groups)])
    if home_dir:
        cmd.extend(['-d', home_dir])
    if bash:
        cmd.extend(['-s', bash])
    if comment:
        cmd.extend(['-c', '"{}"'.format(comment)])
    cmd.append(user)

    status, output = execute(cmd)
    if status != 0 and 'already exists' not in output:
        raise RuntimeError('add user failed, {}'.format(output))


def usermod(user, groups, append=False):
    for group in groups:
        cmd = ['usermod', user, '-G', group, ]
        if append:
            cmd.append('-a')
        status, output = execute(cmd)
        if status != 0 and status != 9:
            raise RuntimeError('run usermod failed, {}'.format(output))


class InitRunner(object):


    def run(self):
        raise NotImplementedError()


NOVA_BASHRC = """
# User specific aliases and functions
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'
# Source global definitions
if [ -f /etc/bashrc ]; then
        . /etc/bashrc
fi
"""

class InitNovaCompute(InitRunner):
    USER = 'nova'
    GROUP = 'nova'
    HOME_DIR = '/var/lib/nova'
    DIR_LIST = ['/etc/nova', '/var/log/nova', '/var/lib/nova/instances',
                '/var/lib/nova/.ssh']

    def makedir(self, *dir_list):
        for directory in dir_list:
            if os.path.exists(directory):
                continue
            os.makedirs(directory)

    def update_libvirtd_conf(self):
        LOG.info('modify libvirtd.conf')
        file_path = '/etc/libvirt/libvirtd.conf'
        old_lines = []
        with open(file_path) as f:
            for line in f.readlines():
                if not line.strip() or line.strip().startswith('#'):
                    old_lines.append(line)
        new_lines = [
            'listen_tls = 0\n',
            'listen_tcp = 1\n',
            'tcp_port = "16509"\n',
            'listen_addr = "0.0.0.0"\n',
            'unix_sock_group = "root"\n',
            'unix_sock_rw_perms = "0777"\n',
            'auth_unix_ro = "none"\n',
            'auth_unix_rw = "none"\n',
            'auth_tcp = "none"\n',
            'max_client_requests = 100\n',
            'admin_max_client_requests = 100\n',
            'log_filters="2:qemu_monitor_json 2:qemu_driver"\n',
            'log_outputs="2:file:/var/log/libvirt/libvirtd.log"\n',
        ]
        with open(file_path, 'w') as f:
            f.writelines(old_lines + new_lines)

    def update_sysconfig_libvirtd(self):
        LOG.info('modify sysconfig libvird')
        file_path = '/etc/sysconfig/libvirtd'
        old_lines = []
        with open(file_path) as f:
            for line in f.readlines():
                if not line.strip() or line.strip().startswith('#'):
                    old_lines.append(line)
        new_lines = [
            'LIBVIRTD_ARGS="--listen"\n',
        ]
        with open(file_path, 'w') as f:
            f.writelines(old_lines + new_lines)

    def create_bashrc(self):
        LOG.info('create .bashrc')
        bashrc_file = os.path.join(self.HOME_DIR, '.bashrc')
        with open(bashrc_file, 'w') as f:
            f.write(NOVA_BASHRC)

    def create_authorized_keys(self):
        LOG.info('copy authorized keys')
        ssh_dir = os.path.join(self.HOME_DIR, '.ssh')
        shutil.copy(os.path.join(WORKSPACE, 'id_rsa'),
                    os.path.join(ssh_dir, 'id_rsa'))
        shutil.copy(os.path.join(WORKSPACE, 'id_rsa.pub'),
                    os.path.join(ssh_dir, 'id_rsa.pub'))
        shutil.copy(os.path.join(WORKSPACE, 'ssh_config'),
                    os.path.join(ssh_dir, 'config'))

        LOG.info('chmod id_rsa')
        execute(['chmod', '600', os.path.join(ssh_dir, 'id_rsa')])

        LOG.info('create authorized_keys')
        with open(os.path.join(WORKSPACE, 'id_rsa.pub'), 'r') as f:
            id_rsa_pub = f.read()
        with open(os.path.join(ssh_dir, 'authorized_keys'), 'w') as f:
            f.write(id_rsa_pub)

    def create_logrotate(self):
        LOG.info('copy logrotate config')
        conf_file = '/etc/logrotate.d/openstack-nova'
        shutil.copy(os.path.join(WORKSPACE, 'openstack-nova.logrotate'),
                    conf_file)

    def chown_directory(self):
        LOG.info('chown nova workspace')
        cmd = ['chown', '-R', '{}:{}'.format(self.USER, self.GROUP),
               self.HOME_DIR, '/etc/nova', '/var/log/nova']
        execute(cmd)

    def run(self):
        groupadd(self.GROUP, gid=162)
        useradd(self.USER, uid=162, gid='nova', groups=['nova', 'nobody'],
                home_dir='/var/lib/nova', bash='/bin/sh',
                comment='OpenStack Nova Daemons')
        usermod(self.USER, ['qemu', 'libvirt'], append=True)

        self.create_bashrc()
        self.makedir(*self.DIR_LIST)
        self.create_authorized_keys()
        self.update_libvirtd_conf()
        self.update_sysconfig_libvirtd()
        self.create_logrotate()
        self.chown_directory()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true',
                        help='show debug messages')
    args = parser.parse_args()

    logging.basicConfig(level=args.debug and logging.DEBUG or logging.INFO,
                        format=FORMAT)
    runner = InitNovaCompute()
    runner.run()


if __name__ == '__main__':
    main()
