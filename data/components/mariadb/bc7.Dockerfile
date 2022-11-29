FROM bclinux7.6

RUN yum clean all \
    && yum -y remove mariadb mariadb-devel mariadb-libs mariadb-common mariadb-config \
    && yum -y install mariadb-server-${VERSION} \
    && yum clean all \
    && mysql_install_db

EXPOSE 3306

ENTRYPOINT [ "/usr/libexec/mysqld", "--user=root", "--datadir=/var/lib/mysql" ]
