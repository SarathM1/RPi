sudo su
ifconfig eth1 192.168.7.1
iptables --table nat --append POSTROUTING --out-interface wlan0 -j MASQUERADE
iptables --append FORWARD --in-interface eth5 -j ACCEPT
echo 1 > /proc/sys/net/ipv4/ip_forward
