FROM bclinux7.6 AS novaComputeBase

ARG VERSION
ARG MIRRORS_BCLINUX_ORG

COPY entrypoint.sh /
COPY *.repo /etc/yum.repos.d/
RUN echo $MIRRORS_BCLINUX_ORG mirrors.bclinux.org >> /etc/hosts \
    && (yum-config-manager --disable extras -q > /dev/null || echo 0) \
    && rpm --rebuilddb \
    && yum -y install python-boto3 python-s3transfer --nogpgcheck \
    && yum -y install python2-cinderclient-2017.$VERSION \
    && yum install -y openstack-nova-compute-2017.$VERSION --nogpgcheck \
    && yum install -y sysfsutils openvswitch python-ovsdbapp --nogpgcheck \
    && yum install -y patch \
    && yum clean all

ENTRYPOINT [ "nova-compute" ]


FROM novaComputeBase

# ARG MIRRORS_BICLINUX_ORG

COPY *.patch /tmp
COPY openssl-1.1.1h.tar.gz /tmp/
COPY google-3.0.0.tar.gz /tmp/
COPY protobuf-3.17.1.tar.gz /tmp/

RUN for patch in $(ls /tmp/*.patch); do patch -d /usr/lib/python2.7/site-packages/ -p1 < ${patch}; done
RUN yum install -y libatomic gcc python-zmq \
    && cd /tmp/ \
    && tar -xzf openssl-1.1.1h.tar.gz \
    && tar -xzf google-3.0.0.tar.gz \
    && tar -xzf protobuf-3.17.1.tar.gz \
    && cd /tmp/openssl-1.1.1h && make && make install && make clean \
    && if [[ ! -f "/usr/lib64/libssl.so.1.1" ]]; then ln -s /usr/local/openssl-1.1.1h/lib/libssl.so.1.1 /usr/lib64/libssl.so.1.1; fi \
    && if [[ ! -f "/usr/lib64/libcrypto.so.1.1" ]]; then ln -s /usr/local/openssl-1.1.1h/lib/libcrypto.so.1.1 /usr/lib64/libcrypto.so.1.1; fi \
    && yum install -y python-beautifulsoup4 \
    && cd /tmp/google-3.0.0 && python setup.py install \
    && cd /tmp/protobuf-3.17.1 && python setup.py install

RUN yum clean all \
    && rm -rf /tmp/*.tar.gz /tmp/openssl-1.1.1h /tmp/google-3.0.0 /tmp/protobuf-3.17.1
