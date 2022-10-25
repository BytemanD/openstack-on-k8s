FROM bclinux7.6

ARG VERSION
ARG MIRRORS_BCLINUX_ORG

COPY *.repo /etc/yum.repos.d/
RUN rm -rf /etc/localtime && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo $MIRRORS_BCLINUX_ORG mirrors.bclinux.org >> /etc/hosts \
    && yum install -y openstack-neutron-2017.${VERSION}.bc.el7 openstack-neutron-ml2-2017.${VERSION}.bc.el7 \
    && yum clean all
RUN systemctl enable neutron-server

EXPOSE 9696

ENTRYPOINT [ "/usr/sbin/init" ]
