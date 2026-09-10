FROM debian:trixie-slim@sha256:109e2c65005bf160609e4ba6acf7783752f8502ad218e298253428690b9eaa4b

WORKDIR /opt/test-runner

COPY requirements.txt requirements.txt
COPY bin/stubs.c /tmp/stubs.c

RUN apt-get update \
    # Install required build and runtime dependencies
    && apt-get install -y --no-install-recommends \
    wget \
    unzip \
    libglib2.0-0t64 \
    libmpfr6 \
    libstdc++6 \
    libxcb1 \
    python3 \
    python3-pip \
    gcc \
    libc6-dev \
    ca-certificates \
    # Compile GUI dependency stubs for loader
    && mkdir -p /usr/local/lib \
    && gcc -shared -fPIC /tmp/stubs.c \
        -o /usr/local/lib/libarturo-stubbed.so \
    && for library in \
        libwebkit2gtk-4.1.so.0 \
        libgtk-3.so.0 \
        libgdk-3.so.0 \
        libjavascriptcoregtk-4.1.so.0; do \
        ln -s libarturo-stubbed.so "/usr/local/lib/${library}"; \
    done \
    && ldconfig \
    # Fetch pre-built release and install it
    && wget --quiet --output-document arturo.zip https://arturo-lang.io/files/arturo-0.10.0-linux-amd64.zip \
    && unzip -d /usr/local/bin arturo.zip arturo \
    && rm arturo.zip \
    # Install unitt test framework
    && arturo --package install unitt 3.0.0 \
    && python3 -m pip install --break-system-packages --no-cache-dir -r requirements.txt \
    # Clean up
    && apt-get purge --auto-remove -y ca-certificates gcc libc6-dev unzip wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /usr/share/icons /usr/share/doc /usr/share/man

COPY bin/run.sh bin/run.sh
COPY parser parser
ENTRYPOINT ["/opt/test-runner/bin/run.sh"]
