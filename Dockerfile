FROM python:3.12-slim

ARG TARGETARCH
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential libxml2-dev libxslt1-dev libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install holehe sherlock-project maigret h8mail

# PhoneInfoga (Go binary), picks the right build for amd64 / arm64
RUN set -e; \
    case "${TARGETARCH:-amd64}" in \
      amd64) A=x86_64 ;; arm64) A=arm64 ;; arm) A=armv7 ;; *) A=x86_64 ;; \
    esac; \
    curl -fsSL "https://github.com/sundowndev/phoneinfoga/releases/latest/download/phoneinfoga_Linux_${A}.tar.gz" \
      | tar -xz -C /usr/local/bin phoneinfoga \
    || echo "phoneinfoga download failed; phone scans will be skipped"

WORKDIR /app
COPY osint_toolkit.py .
VOLUME ["/app/results"]
ENTRYPOINT ["python", "osint_toolkit.py"]
