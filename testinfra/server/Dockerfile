FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive

ARG HEADSCALE_ARCH="arm64"
ARG HEADSCALE_VERSION="0.28.0"

RUN apt-get update && \
    apt-get install -y wget curl jq ca-certificates iputils-ping python3 python3-pip python3-venv tcpdump && \
    wget --output-document=headscale.deb \
    "https://github.com/juanfont/headscale/releases/download/v${HEADSCALE_VERSION}/headscale_${HEADSCALE_VERSION}_linux_${HEADSCALE_ARCH}.deb" && \
    apt-get install -y ./headscale.deb && \
    rm headscale.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/lib/headscale /etc/certs /var/run/headscale

# Prepaer to link ctfproxy package
RUN mkdir -p /app/src
COPY --from=shared_req requirements.txt /app/requirements.txt
RUN python3 -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
RUN pip install -r /app/requirements.txt

COPY init.sh /usr/local/bin/server-init.sh
RUN chmod +x /usr/local/bin/server-init.sh

EXPOSE 4433/tcp 3478/udp 9090/tcp 5555/tcp
CMD sh -c "/usr/local/bin/server-init.sh && python3 -m http.server 5555 & exec headscale serve"
