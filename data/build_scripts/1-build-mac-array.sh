#!/usr/bin/env bash

# A simple array of ip to mac addresses stored in CSV format for easy 
# reading in with other scripts.
mapfile -t ip_list < <(awk '{print $9}' 'iptables_logs/1.txt' | sed 's/SRC=//' | sort -u)

for ip in "${ip_list[@]}"; do
    # Function to generate random mac
    gen_mac=$(printf '%02X:%02X:%02X:%02X:%02X:%02X\n' $((RANDOM%2)) $((RANDOM%8)) $((RANDOM%24)) $((RANDOM%256)) $((RANDOM%256)) $((RANDOM%256)))
    echo -e "$ip,$gen_mac"
done