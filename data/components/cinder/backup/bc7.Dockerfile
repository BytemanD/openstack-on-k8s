# < 5.1.2
# FROM bclinux7.6

# ARG VERSION
# ARG MIRRORS_BCLINUX_ORG

# COPY *.repo /etc/yum.repos.d/
# RUN rm -rf /etc/localtime && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
# RUN echo ${MIRRORS_BCLINUX_ORG} mirrors.bclinux.org >> /etc/hosts \
#     && rpm --rebuilddb \
#     && yum -y install python-boto3 python-s3transfer --nogpgcheck \
#     && yum -y install openstack-cinder-2017.${VERSION} python-pymemcache rbdclient \
#     && yum clean all
# RUN systemctl enable openstack-cinder-backup

# ENTRYPOINT [ "/usr/bin/cinder-backup" ]

# >= 5.1.2
FROM bclinux7.6

ARG VERSION
ARG MIRRORS_BCLINUX_ORG

COPY *.repo /etc/yum.repos.d/
# COPY ebs_cinderdriver-1.0-bcebs.el7.noarch.rpm /tmp

RUN rm -rf /etc/localtime && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo ${MIRRORS_BCLINUX_ORG} mirrors.bclinux.org >> /etc/hosts \
    && rpm --rebuilddb \
    && gt512=$(echo $VERSION |awk -F. '{print $1>=5 && $2>=1 && $3>=2}') \
    && [[ $gt512 -eq 1 ]] && yum -y install grpc \
    && [[ $gt512 -eq 1 ]] && yum -y install ebs_cinderdriver \
    && yum -y install python-boto3 python-s3transfer --nogpgcheck \
    && yum -y install openstack-cinder-2017.${VERSION}.bc.el7 \
    && yum -y install pypthon-novaclient python-pymemcache rbdclient \
    && yum clean all
RUN systemctl enable openstack-cinder-backup

ENTRYPOINT [ "/usr/bin/cinder-backup" ]
