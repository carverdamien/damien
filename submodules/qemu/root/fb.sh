while :
do
clear
find /sys/fs/cgroup/memory/foo/* -name memory.stat -exec grep -HE 'idx|cache' {} \;
sleep 0.1
done
