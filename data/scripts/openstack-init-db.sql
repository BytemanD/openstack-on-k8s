grant all privileges on *.* to 'root'@'localhost' identified by 'root123' with grant option;
grant all privileges on *.* to 'root'@'%' identified by 'root123' with grant option;

grant all privileges on *.* to 'root'@'master-61' identified by 'root123' with grant option;

grant all privileges on *.* to 'root'@'docker-registry' identified by 'root123';

CREATE DATABASE IF NOT EXISTS keystone DEFAULT CHARACTER SET utf8;
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY 'keystone123' with grant option;
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' IDENTIFIED BY 'keystone123' with grant option;

FLUSH privileges;

create database IF NOT EXISTS cinder;


create database IF NOT EXISTS glance;
grant all privileges on glance.* to 'glance'@'localhost' identified by 'glance123' with grant option;
grant all privileges on glance.* to 'glance'@'%' identified by 'glance123' with grant option;


create database IF NOT EXISTS nova_api DEFAULT CHARACTER SET utf8;
create database IF NOT EXISTS nova DEFAULT CHARACTER SET utf8;

grant all privileges on nova.* to 'nova'@'%' identified by 'nova123' with grant option;
grant all privileges on nova.* to 'nova'@'localhost' identified by 'nova123' with grant option;
grant all privileges on nova.* to 'nova'@'mariadb-server' identified by 'nova123' with grant option;
grant all privileges on nova.* to 'nova'@'master-61' identified by 'nova123' with grant option;
grant all privileges on nova.* to 'nova'@'100.73.56.61' identified by 'nova123' with grant option;
grant all privileges on nova.* to 'nova'@'100.73.56.60' identified by 'nova123' with grant option;

grant all privileges on nova_api.* to 'nova'@'%' identified by 'nova123' with grant option;
grant all privileges on nova_api.* to 'nova'@'localhost' identified by 'nova123' with grant option;

grant all privileges on nova_cell0.* to 'nova'@'%' identified by 'nova123' with grant option;
grant all privileges on nova_cell0.* to 'nova'@'localhost' identified by 'nova123' with grant option;


create database IF NOT EXISTS cinder DEFAULT CHARACTER SET utf8;
grant all privileges on cinder.* to 'cinder'@'%' identified by 'cinder123' with grant option;
grant all privileges on cinder.* to 'cinder'@'docker-registry' identified by 'cinder123' with grant option;



create database IF NOT EXISTS neutron2;
grant all privileges on neutron2.* to 'neutron'@'localhost' identified by 'neutron123' with grant option;
grant all privileges on neutron2.* to 'neutron'@'%' identified by 'neutron123' with grant option;


create database IF NOT EXISTS neutron_ovn;
grant all privileges on neutron_ovn.* to 'neutron'@'localhost' identified by 'neutron123' with grant option;
grant all privileges on neutron_ovn.* to 'neutron'@'%' identified by 'neutron123' with grant option;


FLUSH privileges;
