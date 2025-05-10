#!/usr/bin/env bash

apache_logs=$1

# Load IPs and dates from Apache logs
mapfile -t ips < <(awk '{print $1";"$4}' "$apache_logs" | sed 's/\[//g' | sed 's/\:/ /')

declare -A ip_index
while read -r line; do
    IFS=',' read -r ip mac <<< "$line"
    ip_index[$ip]="$mac"
done < mac_array.csv

dst="172.26.15.252"
d_mac="00:15:5d:9c:32:a4"

for i in "${ips[@]}"; do
    IFS=';' read -r ip d <<< "$i"
    echo -e "$(date -d "${d//\//-}" +'%Y-%m-%d %H:%M:%S') [IPTABLES INPUT] ACCEPT IN=eth0 OUT= MAC=$d_mac:${ip_index[$ip]} SRC=$ip DST=$dst LEN=52 TOS=0x00 PREC=0x00 TTL=50 ID=43436 DF PROTO=TCP SPT=$(shuf -i 1024-65535 -n1) DPT=443 WINDOW=114 RES=0x00 ACK URGP=0"
done