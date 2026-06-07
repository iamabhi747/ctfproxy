#!/bin/sh
[ -f /init.txt ] && exit 0

pip install -e /app

# Headscale Test Accounts
headscale user create nat11 --email nat11@deathwing.testnet --display-name "NAT1-Node1"
headscale user create nat12 --email nat12@deathwing.testnet --display-name "NAT1-Node2"
headscale user create nat21 --email nat21@deathwing.testnet --display-name "NAT2-Node1"
headscale user create nat31 --email nat31@deathwing.testnet --display-name "NAT3-Node1"

headscale authkey create --user 1 -e 365d --reusable > /var/lib/authkeys/nat11.txt
headscale authkey create --user 2 -e 365d --reusable > /var/lib/authkeys/nat12.txt
headscale authkey create --user 3 -e 365d --reusable > /var/lib/authkeys/nat21.txt
headscale authkey create --user 4 -e 365d --reusable > /var/lib/authkeys/nat31.txt

touch /init.txt
