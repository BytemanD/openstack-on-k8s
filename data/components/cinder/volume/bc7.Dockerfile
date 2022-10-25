# < 5.1.2
# FROM bclinux7.6

# ARG VERSION
# ARG MIRRORS_BCLINUX_ORG

# COPY *.repo /etc/yum.repos.d/
# RUN rm -rf /etc/localtime && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
# RUN echo ${MIRRORS_BCLINUX_ORG} mirrors.bclinux.org >> /etc/hosts \
#     && rpm --rebuilddb \
#     && yum -y install python-boto3 python-s3transfer --nogpgcheck \
#     && yum -y install openstack-cinder-2017.${VERSION}.bc.el7 python-pymemcache rbdclient \
#     && yum clean all
# RUN systemctl enable openstack-cinder-volume

# ENTRYPOINT [ "/usr/bin/cinder-volume" ]

# >= 5.1.2
# FROM bclinux7.6

# ARG VERSION
# ARG MIRRORS_BCLINUX_ORG

# COPY *.repo /etc/yum.repos.d/
# RUN rm -rf /etc/localtime && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
# RUN echo ${MIRRORS_BCLINUX_ORG} mirrors.bclinux.org >> /etc/hosts \
#     && rpm --rebuilddb \
#     && yum -y install python-boto3 python-s3transfer --nogpgcheck \
#     && yum -y install ebs_cinderdriver \
#     && yum -y install openstack-cinder-2017.${VERSION}\
#     && yum clean all
# RUN systemctl enable openstack-cinder-volume

# ENTRYPOINT [ "/usr/bin/cinder-volume" ]

# >= 5.2.0
FROM bclinux7.6

ARG VERSION
ARG MIRRORS_BCLINUX_ORG

COPY *.repo /etc/yum.repos.d/
COPY volume_api_pb2.tar.gz /usr/local/lib/

RUN rm -rf /etc/localtime && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo ${MIRRORS_BCLINUX_ORG} mirrors.bclinux.org >> /etc/hosts \
    && cd /usr/local/lib/ && tar -xzf volume_api_pb2.tar.gz \
    && yum install -y grpc-1.0 \
    && rpm --rebuilddb \
    && yum -y install python-boto3 python-s3transfer --nogpgcheck \
    && yum -y install ebs_cinderdriver \
    && yum -y install openstack-cinder-2017.${VERSION}.bc.el7 \
    && yum clean all
RUN systemctl enable openstack-cinder-volume

ENTRYPOINT [ "/usr/bin/cinder-volume" ]

