FROM bclinux7.6

ARG VERSION
ARG MIRRORS_BCLINUX_ORG

COPY *.repo /etc/yum.repos.d/
RUN rm -rf /etc/localtime && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo ${MIRRORS_BCLINUX_ORG} mirrors.bclinux.org >> /etc/hosts \
    && rpm --rebuilddb \
    && yum -y install python-boto3 python-s3transfer --nogpgcheck \
    && yum install -y openstack-nova-console-2017.$VERSION.bc.el7 --nogpgcheck \
    && yum clean all
RUN systemctl enable openstack-nova-consoleauth

ENTRYPOINT [ "/usr/bin/nova-consoleauth" ]

