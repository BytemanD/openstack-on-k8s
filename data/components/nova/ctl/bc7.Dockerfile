FROM bclinux7

ARG VERSION
ARG MIRRORS_BCLINUX_ORG

COPY *.repo /etc/yum.repos.d/
RUN rm -rf /etc/localtime && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo ${MIRRORS_BCLINUX_ORG} mirrors.bclinux.org >> /etc/hosts \
    && rpm --rebuilddb \
    && (yum remove -y python-nova || echo 0) \
    && yum -y install python-boto3 python-s3transfer --nogpgcheck \
    && yum install -y openstack-nova-api-2017.${VERSION}.bc.el7 --nogpgcheck \
    && yum install -y openstack-nova-scheduler-2017.${VERSION}.bc.el7 --nogpgcheck \
    && yum install -y openstack-nova-conductor-2017.${VERSION}.bc.el7 --nogpgcheck \
    && yum install -y patch \
    && yum clean all
RUN systemctl enable openstack-nova-api openstack-nova-scheduler openstack-nova-conductor

EXPOSE 8774

ENTRYPOINT [ "/usr/sbin/init" ]
