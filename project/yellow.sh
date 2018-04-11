#!/bin/bash



echo -e "Please enter the \033[1;32mmain IP\033[0m: "
read serverip
echo -e "Default IP is now set on \033[1;32m$serverip\033[0m\n"


# Phase 1

echo -e "\n\033[0;31m--------------------------------\033[0m" 2> /dev/null
echo -e "Launching the first example..." 2> /dev/null
client/main.py $serverip &> /dev/null &
echo -e "\033[1;32m 1 client is launched\033[0m" 2> /dev/null
echo -e "\033[1;31mPress enter to go to the next one\033[0m\n" 2> /dev/null
read &> /dev/null
kill $(jobs -rp) &> /dev/null
wait $(jobs -rp) 2>/dev/null



# Phase 2
echo -e "\033[0;31m--------------------------------\033[0m" 2> /dev/null
echo -e "Launching the second example..." 2> /dev/null
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
server/main.py $serverip 3 6 4 2 --nodes 9 12 13 14 15 16 17 &> /dev/null &
echo -e "\033[1;32m1 server process with \033[1;33m7 nodes\033[0m is launched.\033[0m Please launch the phase 3 on remote computers." 2> /dev/null
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
server/main.py $serverip 4 4 2 2 --nodes 4 8 &> /dev/null &
server/main.py $serverip 4 4 2 2 --nodes 13 14 &> /dev/null &
echo -e "\033[1;32m2 servers processes with \033[1;33m2 nodes each\033[0m are launched.\033[0m Please launch the phase 4 on remote computers." 2> /dev/null
read &> /dev/null
client/main.py $serverip &> /dev/null &
client/main.py $serverip &> /dev/null &
echo -e "\033[1;32m2 clients are launched\033[0m" 2> /dev/null
echo -e "\033[1;31mPress enter to go to finish\033[0m" 2> /dev/null
read &> /dev/null
kill $(jobs -rp) &> /dev/null
wait $(jobs -rp) 2>/dev/null


