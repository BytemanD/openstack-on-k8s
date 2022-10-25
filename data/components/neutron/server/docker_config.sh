yum install openvswitch-ovn-host openvswitch-ovn-central




# [DEFAULT]
# core_plugin = neutron.plugins.ml2.plugin.Ml2Plugin
# service_plugins = trunk,qos,networking_ovn.l3.l3_ovn.OVNL3RouterPlugin
# [qos]
# notification_drivers = ovn-qos


# vi /etc/neutron/plugins/ml2/ml2_conf.ini
# b. 编辑配置文件。
# [ml2]
# type_drivers = local,flat,vlan,geneve
# tenant_network_types =geneve,vlan
# mechanism_drivers = ovn
# extension_drivers = port_security,qos,dns
# overlay_ip_version = 6

# [ml2_type_flat]
# [ml2_type_gre]
# ###根据实际vlan分配情况补充
# #[ml2_type_vxlan]
# #vni_ranges= 1:100000
# [ml2_type_vlan]
# network_vlan_ranges = 计算节点br-provider网桥映射名称:10:4000
# [ml2_type_geneve]
# vni_ranges = 1:65536
# max_header_size = 38
# [securitygroup]
# enable_security_group = true
# [ovn]
# ovn_nb_connection = tcp:OVN节点VIP:6641
# ovn_sb_connection = tcp:OVN节点VIP:6642
# ovn_l3_scheduler = leastloaded
