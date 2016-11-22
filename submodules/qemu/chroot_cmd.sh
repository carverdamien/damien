#!/bin/bash
set -e -x

# No password
sed -i '/^root/ { s/:x:/::/ }' /etc/passwd
# Autologin
echo 'V0:23:respawn:/bin/login -f root tty1 < /dev/hvc0 >/dev/hvc0 2>&1' | 
tee -a /etc/inittab
# Automatically bring up eth0 using DHCP
printf '\nauto eth0\niface eth0 inet dhcp\n' | 
tee -a /etc/network/interfaces
# Add jessie
echo 'deb http://ftp.de.debian.org/debian jessie main' |
tee -a /etc/apt/sources.list
# Add sshkey
mkdir -p /root/.ssh/
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCzbswl/H/28EBVFVZZ+9t2aMcknXelbodTL1oOAuj7cHfnwH9P+fmKnLTJpHG9i3PpLQ2LdreRDl8mrYUppiePnT4MTOT0CPeBBGvDJS6j1MfGgFAJka+xOgy9iODoKM4a3rHUpV4hzk2TsmrmaGb1zapOPLM79aN+buCBwj+B5Uz1qaO0jMgrbIj7gwPYdONiMpqgR0diaodjwnq48lYaecgxYZ1zKfODBMVT2EjnU+WmkZclP2z99EdV5J4Fe+1bgGkD3Eu5aJt06/vk5RxZSV1Aa3DiCfr5/Qti7Klx0Qcw7PYtjJavIFgRHize89/c8PImyFiOAmqiw3IdRX1h dc@dc-Precision-T1700" | tee /root/.ssh/authorized_keys
# Add Docker
apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
echo 'deb https://apt.dockerproject.org/repo debian-jessie main' |
tee -a /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-engine
service docker stop
wget -O /usr/bin/docker https://get.docker.com/builds/Linux/x86_64/docker-1.10.0
wget -O /usr/local/bin/docker-compose https://github.com/docker/compose/releases/download/1.7.0/docker-compose-`uname -s`-`uname -m`
chmod +x /usr/local/bin/docker-compose
