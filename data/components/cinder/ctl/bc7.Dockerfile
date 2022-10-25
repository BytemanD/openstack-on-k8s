FROM bclinux7.6

ARG VERSION
ARG MIRRORS_BCLINUX_ORG

COPY *.repo /etc/yum.repos.d/
RUN rm -rf /etc/localtime && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo ${MIRRORS_BCLINUX_ORG} mirrors.bclinux.org >> /etc/hosts \
    && rpm --rebuilddb \
    && yum -y install python-boto3 python-s3transfer --nogpgcheck \
    && yum -y install openstack-cinder-2017.${VERSION}.bc.el7 python-pymemcache \
    && yum clean all
RUN systemctl enable openstack-cinder-api.service openstack-cinder-scheduler.service

EXPOSE 9292
ENTRYPOINT [ "/usr/sbin/init" ]
