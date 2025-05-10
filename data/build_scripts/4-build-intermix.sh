#!/usr/bin/env bash

# Intermix the iptables logs
cat iptables_logs/scan.txt iptables_logs/1.txt > iptables_logs/combined.txt
grep "2015-05-17" iptables_logs/combined.txt | sort -k 2 > iptables_logs/sorted.txt
head -n 1000 iptables_logs/sorted.txt > iptables_logs/sorted_1000.txt
head -n 250 iptables_logs/sorted.txt > iptables_logs/sorted_250.txt