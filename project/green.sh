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
client/main.py $serverip &> /dev/null &
client/main.py $serverip &> /dev/null &
echo -e "\033[1;32m2 clients are launched\033[0m" 2> /dev/null
echo -e "\033[1;31mPress enter to go to finish\033[0m" 2> /dev/null
read &> /dev/null
kill $(jobs -rp) &> /dev/null
wait $(jobs -rp) 2>/dev/null


