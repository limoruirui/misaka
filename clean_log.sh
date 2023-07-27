#!/bin/sh
echo "=================== start clean qinglong  logs ==========================" 
 
logs=$(find /var/log/nginx/*.log)
 
for log in $logs; 
do
    echo "clean logs:" 
    echo $log
    cat /dev/null> $log
done
 
echo "==================== end clean qinglong logs =========================="
