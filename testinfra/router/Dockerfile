FROM alpine:latest

RUN apk add --no-cache wget curl iptables iproute2 iputils-ping jq tcpdump

COPY init.sh /usr/local/bin/router-init.sh
RUN chmod +x /usr/local/bin/router-init.sh

ENTRYPOINT ["/usr/local/bin/router-init.sh"]
