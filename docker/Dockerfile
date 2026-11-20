ARG BASE_IMAGE=debian:12-slim@sha256:734a72b3d6142a71993b4bc580ca01d8ca687f77a2c422d96a961d3376b179bc
ARG FLYE_VERSION=2.9.7
ARG FLYE_SOURCE_SHA256=041635b3b7e7afc69fd50ab9cbf040db4749b04ae626ba65c8b08f550642351f

# Source tag 2.9.7 resolves to f52d39b967441e4b6572d94878b84505f17edb90.
# The base and source bytes are pinned; Debian bookworm/security APT repositories
# remain rolling. Package revisions/availability may change, so later rebuilds
# are not byte-identical. Keep the validated image digest; if a repository drifts,
# review its replacement and revalidate both architectures instead of bypassing
# source checksums or silently substituting an unreviewed source/dependency.
FROM ${BASE_IMAGE} AS builder
ARG FLYE_VERSION
ARG FLYE_SOURCE_SHA256
ENV DEBIAN_FRONTEND=noninteractive
RUN set -eux; \
    apt-get -o Acquire::Retries=3 update; \
    apt-get -o Acquire::Retries=3 install -y --no-install-recommends \
      build-essential ca-certificates curl python3 python3-pip \
      python3-setuptools python3-wheel zlib1g-dev; \
    rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/build/flye
RUN set -eux; \
    curl --retry 5 --retry-delay 2 --retry-all-errors --connect-timeout 30 -fsSL \
      "https://github.com/mikolmogorov/Flye/archive/refs/tags/${FLYE_VERSION}.tar.gz" -o flye.tar.gz; \
    echo "${FLYE_SOURCE_SHA256}  flye.tar.gz" | sha256sum -c -; \
    tar -xzf flye.tar.gz --strip-components=1; \
    test "$(grep -Fxc 'ifeq ($(shell uname -m),arm64)' Makefile)" = 1; \
    sed -i 's/ifeq ($(shell uname -m),arm64)/ifneq (,$(filter $(shell uname -m),arm64 aarch64))/' Makefile; \
    python3 -m pip install --no-cache-dir --no-deps --no-build-isolation \
      --break-system-packages --prefix=/opt/flye .; \
    install -d /opt/flye/share/doc/flye/third-party; \
    install -m 0644 README.md LICENSE docs/INSTALL.md docs/USAGE.md docs/FAQ.md docs/NEWS.md \
      /opt/flye/share/doc/flye/; \
    cp --parents lib/libcuckoo/LICENSE lib/interval_tree/LICENSE lib/lemon/LICENSE \
      lib/minimap2/LICENSE.txt lib/samtools-1.9/LICENSE \
      lib/samtools-1.9/htslib-1.9/LICENSE lib/samtools-1.9/lz4/LICENSE \
      /opt/flye/share/doc/flye/third-party/; \
    find /opt/flye -type f -name '*.pyc' -delete; \
    for binary in /opt/flye/local/bin/flye-modules /opt/flye/local/bin/flye-minimap2 /opt/flye/local/bin/flye-samtools; do \
      strip --strip-debug "$binary"; \
    done
# The only upstream change above is the existing architecture-name build fix:
# use Flye's own ARM NEON path for Linux aarch64 as well as arm64. No algorithm,
# model, threshold or runtime Python source is patched.

FROM ${BASE_IMAGE}
ENV DEBIAN_FRONTEND=noninteractive
RUN set -eux; \
    apt-get -o Acquire::Retries=3 update; \
    apt-get -o Acquire::Retries=3 install -y --no-install-recommends \
      bash ca-certificates gzip libgcc-s1 libstdc++6 python3 zlib1g; \
    rm -rf /var/lib/apt/lists/*
COPY --from=builder /opt/flye/ /opt/flye/
COPY docker/flye-smoke.py /usr/local/libexec/flye-smoke.py
ENV PATH=/opt/flye/local/bin:/opt/flye/bin:${PATH}
ENV PYTHONPATH=/opt/flye/local/lib/python3.11/dist-packages:/opt/flye/local/lib/python3.11/site-packages:/opt/flye/lib/python3.11/site-packages:/opt/flye/lib/python3.11/dist-packages
ENV PYTHONDONTWRITEBYTECODE=1
# Stable, offline loading/identity/link checks only. Full toy assembly, resume,
# shared inputs and negative cases run after the build on both native platforms.
# This avoids making ARM64 image publication depend on heavy workflow timing.
RUN python3 /usr/local/libexec/flye-smoke.py identity
WORKDIR /tmp
ENV TAFFISH_ENV=TAFFISH
ENV TAFFISH_NAME=flye
