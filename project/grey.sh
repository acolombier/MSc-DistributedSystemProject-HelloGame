#!/bin/bash



serverip="localhost"

echo -e "The machine IP is \033[1;32m$(ifconfig | grep wls -A1 | tail -n 1 | cut -d':' -f 2 | cut -d' ' -f 1)\033[0m\n"

# Phase 1

echo -e "\033[0;31m--------------------------------\033[0m" 2> /dev/null
echo -e "Launching the first example..." 2> /dev/null
server/main.py $serverip 2 2 4 4 &> /dev/null &
echo -e "\033[1;32m 1 server process with \033[1;33m4 nodes\033[0m is launched\033[0m" 2> /dev/null
client/main.py $serverip &> /dev/null &
echo -e "\033[1;32m 1 client is launched\033[0m" 2> /dev/null
echo -e "\033[1;31mPress enter to go to the next one\033[0m\n" 2> /dev/null
read &> /dev/null
kill $(jobs -rp) &> /dev/null
wait $(jobs -rp) 2>/dev/null



# Phase 2
echo -e "\033[0;31m--------------------------------\033[0m" 2> /dev/null
echo -e "Launching the second example..." 2> /dev/null
server/main.py $serverip 5 2 3 4 --nodes 0 2 3 7 8 9 &> /dev/null &
server/main.py $serverip 5 2 3 4 --nodes 1 4 6 &> /dev/null &
server/main.py $serverip 5 2 3 4 --nodes 5 &> /dev/null &
echo -e "\033[1;32m3 servers processes with \033[1;33m6 nodes\033[0m, \033[1;33m3 nodes\033[0m and \033[1;33m1 nodes\033[0m are launched\033[0m" 2> /dev/null
client/main.py $serverip &> /dev/null &
client/main.py $serverip &> /dev/null &
echo -e "\033[1;32m2 clients are launched\033[0m" 2> /dev/null
echo -e "\033[1;31mPress enter to go to the next one\033[0m\n" 2> /dev/null
read &> /dev/null
kill $(jobs -rp) &> /dev/null
wait $(jobs -rp) 2>/dev/null


# Phase 3
echo -e "\033[0;31m--------------------------------\033[0m" 2> /dev/null
echo -e "Launching the third example..." 2> /dev/null
server/main.py $serverip 3 6 4 2 --nodes 0 3 5 7 10 11 &> /dev/null &
server/main.py $serverip 3 6 4 2 --nodes 1 2 4 6 8 &> /dev/null &
echo -e "\033[1;32m2 servers processes with \033[1;33m6 nodes\033[0m, and \033[1;33m5 node\033[0m are launched.\033[0m Please launch the phase 3 on remote computers." 2> /dev/null
read &> /dev/null
client/main.py $serverip &> /dev/null &
client/main.py $serverip &> /dev/null &
echo -e "\033[1;32m2 clients are launched\033[0m" 2> /dev/null
echo -e "\033[1;31mPress enter to go to the next one\033[0m\n" 2> /dev/null
read &> /dev/null
kill $(jobs -rp) &> /dev/null
wait $(jobs -rp) 2>/dev/null


# Phase 4 
echo -e "\033[0;31m--------------------------------\033[0m" 2> /dev/null
echo -e "Launching the fourth example..." 2> /dev/null
server/main.py $serverip 4 4 2 2 --nodes 1 2 &> /dev/null &
server/main.py $serverip 4 4 2 2 --nodes 7 11 &> /dev/null &
echo -e "\033[1;32m2 servers processes with \033[1;33m2 nodes each\033[0m are launched.\033[0m Please launch the phase 4 on remote computers." 2> /dev/null
read &> /dev/null
client/main.py $serverip &> /dev/null &
client/main.py $serverip &> /dev/null &
echo -e "\033[1;32m2 clients are launched\033[0m" 2> /dev/null
echo -e "\033[1;31mPress enter to go to finish\033[0m" 2> /dev/null
read &> /dev/null
kill $(jobs -rp) &> /dev/null
wait $(jobs -rp) 2>/dev/null


