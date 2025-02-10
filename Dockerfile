FROM nimlang/nim:2.2.0-ubuntu

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y jq build-essential git libgtk-3-dev libwebkit2gtk-4.0-dev libmpfr-dev && \
    apt-get purge --auto-remove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/arturo-lang/arturo.git

RUN cd arturo && ./build.nims build --install --log && \
    cd .. && rm -rf arturo

ENV PATH="/root/.arturo/bin:${PATH}"

RUN arturo --package install unitt 1.1.2

WORKDIR /opt/test-runner
COPY bin/run.sh bin/run.sh
ENTRYPOINT ["/opt/test-runner/bin/run.sh"]
