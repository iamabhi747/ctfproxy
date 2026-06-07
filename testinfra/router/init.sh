#!/bin/sh

# Apply Source NAT (Masquerade) for the configured subnet
if [ -z "$SUBNET" ]; then
    echo "Warning: SUBNET environment variable not set. NAT might not function."
else
    iptables -t nat -A POSTROUTING -s "$SUBNET" -j MASQUERADE
fi

# Keep the container alive cleanly without polling loops
exec tail -f /dev/null
