FROM python:3.13.11-slim-trixie

RUN apt-get update \
    # Install required build and runtime dependencies
    && apt-get install -y --no-install-recommends \
    wget \
    unzip \
    libmpfr6 \
    libwebkit2gtk-4.1-0 \
    ca-certificates \
    # Fetch pre-built release and install it
    && wget --quiet --output-document arturo.zip https://arturo-lang.io/files/arturo-0.10.0-linux-amd64.zip \
    && unzip -d /usr/local/bin arturo.zip arturo \
    && rm arturo.zip \
    # Install unitt test framework
    && arturo --package install unitt 3.0.0 \
    # Clean up
    && apt-get purge --auto-remove -y wget unzip ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /usr/share/icons /usr/share/doc /usr/share/man

WORKDIR /opt/test-runner
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY bin/run.sh bin/run.sh
COPY parser parser
ENTRYPOINT ["/opt/test-runner/bin/run.sh"]
