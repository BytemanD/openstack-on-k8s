FROM bclinux7.6

ARG VERSION
ARG MIRRORS_BCLINUX_ORG

COPY *.repo /etc/yum.repos.d/
RUN echo ${MIRRORS_BCLINUX_ORG} mirrors.bclinux.org >> /etc/hosts \
    && rpm --rebuilddb \
    && yum -y install python-boto3 python-s3transfer --nogpgcheck \
    && yum -y install openstack-keystone-2017.${VERSION}.bc.el7 \
    && yum -y install httpd mod_wsgi python-memcached \
    && yum clean all
RUN cp /usr/share/keystone/wsgi-keystone.conf /etc/httpd/conf.d/ \
    && sed -i 's|^#ServerName .*|ServerName 0.0.0.0|g' /etc/httpd/conf/httpd.conf \
    && rm -rf /etc/localtime && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN keystone-manage credential_setup --keystone-user keystone --keystone-group keystone \
    && keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone

RUN systemctl enable httpd

EXPOSE 35357 5000
ENTRYPOINT [ "/usr/sbin/httpd" ]
