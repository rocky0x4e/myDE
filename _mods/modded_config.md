#
https://forums.linuxmint.com/viewtopic.php?t=335848
sudo vi /etc/pam.d/common-auth 
sudo vi /etc/pam.d/common-password 
sudo vi /etc/pam.d/common-session 
sudo vi /etc/pam.d/common-session-noninteractive

#

# best DNSSEC setup to enable DNSSEC on default interface but not tun (VPN - because it might not work with VPN)
## /etc/systemd/resolved.conf
DNS=1.1.1.1 9.9.9.9
FallbackDNS=208.67.220.220
#Domains=
DNSSEC=no
DNSOverTLS=no
MulticastDNS=no

## /etc/systemd/network/10-wlp1s0.network
[Match]
Name=wlp1s0

[Network]
DNS=1.1.1.1 9.9.9.9
DNSSEC=yes
DNSOverTLS=yes


