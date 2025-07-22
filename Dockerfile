FROM ubuntu:24.04

RUN apt-get update \
 # Install required build and runtime dependencies, cannot use `--no-install-recommends`
 && apt-get install -y jq wget unzip libmpfr6 libwebkit2gtk-4.1-0 libpcre3 \
 # Fetch pre-built nightly release and install it
 && wget --quiet --output-document arturo.zip https://github.com/arturo-lang/nightly/releases/download/2025-04-01/arturo-nightly.2025-03-31-amd64-linux-full.zip \
 && unzip -d /usr/local/bin arturo.zip arturo \
 && rm arturo.zip \
 # Install unitt test framework
 && arturo --package install unitt 2.0.1 \
 # Clean up apt-get and build dependencies: python3 was installed but not necessary for runtime
 && apt-get purge --auto-remove -y wget unzip python3 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
 # Remove 30MB of icons that are not necessary
 && rm -rf /usr/share/icons

WORKDIR /opt/test-runner
COPY bin/run.sh bin/run.sh
ENTRYPOINT ["/opt/test-runner/bin/run.sh"]
