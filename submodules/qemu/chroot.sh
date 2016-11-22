#!/bin/bash
set -e -x
main() {
sudo cp -a debootstrap chroot
cat_cmd | sudo chroot chroot
}
cat_cmd() {
cat <<EOF
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
echo "$(cat ~/.ssh/id_rsa.pub)" | tee /root/.ssh/authorized_keys
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
EOF
}
cat_cmd
main
