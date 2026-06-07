FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y wget curl jq ca-certificates iproute2 iptables iputils-ping tcpdump python3 python3-pip python3-venv && \
    curl -fsSL https://tailscale.com/install.sh | sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/lib/tailscale /var/run/tailscale

# Prepaer to link ctfproxy package
RUN mkdir -p /app/src
COPY --from=shared_req requirements.txt /app/requirements.txt
RUN python3 -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
RUN pip install -r /app/requirements.txt

