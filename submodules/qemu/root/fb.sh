while :
do
clear
find /sys/fs/cgroup/memory -name memory.stat -exec grep -HE 'bm|cache' {} \;
sleep 0.1
done
