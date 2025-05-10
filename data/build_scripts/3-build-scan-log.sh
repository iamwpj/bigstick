#!/usr/bin/env bash

# Generate a series of denies from iptables logs
# as if you were scanning a host.
# 
# This will create a dedicated block by one
# specific IP and then randomize the rest.

declare -a output
scan_ports=(
    21 22 25 53 69 110 123 389 445 465 631 636 993 3306 3389 8080  
)

# All of these events happen on the same day
date_y=2015
date_m=05
date_d=17

# Our target host
dst=172.26.15.252
d_mac=00:15:5d:9c:32:a4

function bad_actor {

    # This is done to hard-code a block within the dataset of 
    # one IP scanning.
    declare -A ip_index
    while read -r line; do
        IFS=',' read -r ip mac <<< "$line"
        ip_index[$ip]="$mac"
    done < mac_array.csv

    src=93.164.60.142 # this is the bad-actor
    s_mac=${ip_index[$src]}
    date_H=11  

    # Nov 20 20:48:11 check.it-nis.uni.edu kernel: [IPTABLES INPUT] dropped IN=eth0 OUT= MAC=00:50:56:a7:6b:44:00:50:56:a7:a6:40:08:00 SRC=10.120.0.20 DST=10.120.0.33 LEN=60 TOS=0x00 PREC=0x00 TTL=64 ID=15619 DF PROTO=TCP SPT=49756 DPT=1058 WINDOW=32120 RES=0x00 SYN URGP=0
    for port in "${scan_ports[@]}"; do
        # We lock this to our current datetime with a delay to simulate a busy CPU. I know I could simulate this, but eh.
        sleep 0.$((RANDOM % 10))
        date_MS=$(date +"%M:%S")
        output+=("$date_y-$date_m-$date_d $date_H:$date_MS [IPTABLES INPUT] REJECT IN=eth0 OUT= MAC=$d_mac:$s_mac SRC=$src DST=$dst LEN=60 TOS=0x00 PREC=0x00 TTL=64 ID=15619 DF PROTO=TCP SPT=$(shuf -i 1024-65535 -n1) DPT=$port WINDOW=32120 RES=0x00 SYN URGP=0")
    done
}


function random_scans {
    declare -a random_ips
    for _ in {1..512}; do
        random_ips+=("$(printf "%d.%d.%d.%d\n" "$((RANDOM % 256))" "$((RANDOM % 256))" "$((RANDOM % 256))" "$((RANDOM % 256))")")
    done

    for ip in "${random_ips[@]}"; do
        # Not too random MACs :shrug:
        s_mac=$(printf '%02X:%02X:%02X:%02X:%02X:%02X\n' $((RANDOM % 8)) $((RANDOM % 8)) $((RANDOM % 256)) $((RANDOM % 256)) $((RANDOM % 256)) $((RANDOM % 256)))

        date_H=$(printf "%02d" "$(shuf -i 10-23 -n1)")
        date_M=$(printf "%02d" $((RANDOM % 60)))
        date_S=$(printf "%02d" $((RANDOM % 60)))
        port=${scan_ports[$((RANDOM % ${#scan_ports[@]}))]}

        output+=("$date_y-$date_m-$date_d $date_H:$date_M:$date_S [IPTABLES INPUT] REJECT IN=eth0 OUT= MAC=$d_mac:$s_mac SRC=$ip DST=$dst LEN=60 TOS=0x00 PREC=0x00 TTL=64 ID=15619 DF PROTO=TCP SPT=$(shuf -i 1024-65535 -n1) DPT=$port WINDOW=32120 RES=0x00 SYN URGP=0")

    done
}

random_scans
bad_actor
readarray -t sorted < <(printf '%s\0' "${output[@]}" | sort -z | xargs -0n1)
printf "%s\n" "${sorted[@]}"