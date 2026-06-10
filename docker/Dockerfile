ARG FLYE_VERSION=2.9.6
ARG FLYE_BUILD=1802
ARG FLYE_SOURCE_SHA256=f05a3889b1c7aafed4cc0ed1adc1f19c22618c1c7b97ab5f80d388c8192bd32a
ARG DEBIAN_MIRROR=http://deb.debian.org/debian
ARG DEBIAN_SECURITY_MIRROR=http://deb.debian.org/debian-security

FROM debian:12-slim AS builder

ARG FLYE_VERSION
ARG FLYE_BUILD
ARG FLYE_SOURCE_SHA256
ARG DEBIAN_MIRROR
ARG DEBIAN_SECURITY_MIRROR

ENV DEBIAN_FRONTEND=noninteractive

RUN set -eux; \
    sed -i \
      -e "s|http://deb.debian.org/debian-security|${DEBIAN_SECURITY_MIRROR}|g" \
      -e "s|http://deb.debian.org/debian|${DEBIAN_MIRROR}|g" \
      /etc/apt/sources.list.d/debian.sources; \
    for attempt in 1 2 3 4 5 6; do \
      if apt-get -o Acquire::Retries=3 update \
       && apt-get -o Acquire::Retries=3 install -y --no-install-recommends \
            build-essential \
            ca-certificates \
            curl \
            make \
            python3 \
            python3-pip \
            python3-setuptools \
            zlib1g-dev; then \
        break; \
      fi; \
      if [ "$attempt" = "6" ]; then exit 1; fi; \
      apt-get clean; \
      rm -rf /var/lib/apt/lists/*; \
      sleep 5; \
    done; \
    rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/build/flye

ENV PATH=/opt/flye/local/bin:/opt/flye/bin:${PATH}
ENV PYTHONPATH=/opt/flye/local/lib/python3.11/dist-packages:/opt/flye/local/lib/python3.11/site-packages:/opt/flye/lib/python3.11/site-packages:/opt/flye/lib/python3.11/dist-packages

RUN set -eux; \
    curl --retry 5 --retry-delay 2 --retry-all-errors -fsSL \
      "https://github.com/mikolmogorov/Flye/archive/refs/tags/${FLYE_VERSION}.tar.gz" \
      -o flye.tar.gz; \
    echo "${FLYE_SOURCE_SHA256}  flye.tar.gz" | sha256sum -c -; \
    tar -xzf flye.tar.gz --strip-components=1; \
    sed -i 's/ifeq ($(shell uname -m),arm64)/ifneq (,$(filter $(shell uname -m),arm64 aarch64))/' Makefile; \
    python3 -m pip install --no-cache-dir --break-system-packages --prefix=/opt/flye .; \
    flye --version 2>&1 | grep -Fx "${FLYE_VERSION}-b${FLYE_BUILD}" >/dev/null; \
    flye --help 2>&1 | grep -F "Assembly of long reads with repeat graphs" >/dev/null; \
    python3 -m flye.tests.test_toy; \
    install -d /opt/flye/share/doc/flye; \
    install -m 0644 README.md LICENSE docs/INSTALL.md docs/USAGE.md docs/FAQ.md docs/NEWS.md \
      /opt/flye/share/doc/flye/

FROM debian:12-slim

ARG FLYE_VERSION
ARG FLYE_BUILD
ARG DEBIAN_MIRROR
ARG DEBIAN_SECURITY_MIRROR

ENV DEBIAN_FRONTEND=noninteractive

RUN set -eux; \
    sed -i \
      -e "s|http://deb.debian.org/debian-security|${DEBIAN_SECURITY_MIRROR}|g" \
      -e "s|http://deb.debian.org/debian|${DEBIAN_MIRROR}|g" \
      /etc/apt/sources.list.d/debian.sources; \
    for attempt in 1 2 3 4 5 6; do \
      if apt-get -o Acquire::Retries=3 update \
       && apt-get -o Acquire::Retries=3 install -y --no-install-recommends \
            bash \
            ca-certificates \
            gzip \
            libgcc-s1 \
            libstdc++6 \
            python3 \
            zlib1g; then \
        break; \
      fi; \
      if [ "$attempt" = "6" ]; then exit 1; fi; \
      apt-get clean; \
      rm -rf /var/lib/apt/lists/*; \
      sleep 5; \
    done; \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/flye/ /opt/flye/

ENV PATH=/opt/flye/local/bin:/opt/flye/bin:${PATH}
ENV PYTHONPATH=/opt/flye/local/lib/python3.11/dist-packages:/opt/flye/local/lib/python3.11/site-packages:/opt/flye/lib/python3.11/site-packages:/opt/flye/lib/python3.11/dist-packages

RUN set -eux; \
    flye --version 2>&1 | grep -Fx "${FLYE_VERSION}-b${FLYE_BUILD}" >/dev/null; \
    flye --help 2>&1 | grep -F "Assembly of long reads with repeat graphs" >/dev/null; \
    python3 -c 'from flye.__version__ import __version__; assert __version__ == "2.9.6"'; \
    command -v flye-modules; \
    command -v flye-minimap2; \
    command -v flye-samtools; \
    for x in flye-modules flye-minimap2 flye-samtools; do \
      ! ldd "$(command -v "$x")" 2>&1 | grep -F "not found" >/dev/null; \
    done

RUN set -eux; \
    tmp=/tmp/flye-check; \
    rm -rf "$tmp"; \
    mkdir -p "$tmp"; \
    cd "$tmp"; \
    python3 -m flye.tests.test_toy > toy.log 2>&1; \
    grep -F "TEST SUCCESSFUL" toy.log >/dev/null; \
    rm -rf "$tmp"

WORKDIR /root

ENV TAFFISH_ENV=TAFFISH
ENV TAFFISH_NAME=flye
