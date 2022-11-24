FROM bclinux7

ARG VERSION
ARG MIRRORS_BCLINUX_ORG

# RUN mkdir /k8stack

COPY id_rsa /k8stack/
COPY id_rsa.pub /k8stack/
COPY init-utils.py /k8stack/

COPY *.repo /etc/yum.repos.d/

RUN echo $MIRRORS_BCLINUX_ORG mirrors.bclinux.org >> /etc/hosts \
    && (yum-config-manager --disable extras -q > /dev/null || echo 0) \
    && rpm --rebuilddb \
    && yum -y install python-boto3 python-s3transfer --nogpgcheck \
    && yum install -y openstack-nova-compute-2017.$VERSION.bc.el7 --nogpgcheck \
    && yum install -y sysfsutils openvswitch python-ovsdbapp --nogpgcheck \
    && yum install -y patch \
    && yum clean all

ENTRYPOINT [ "nova-compute" ]
