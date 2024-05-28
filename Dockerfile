FROM alpine:3.20.0 AS build

RUN apk add --no-cache curl

ARG VERSION=0.9.83
ARG TAG=2024-05-28
ARG ARCHIVE="arturo-${VERSION}-${TAG}-Linux-full.tar.gz"

WORKDIR /root/.arturo/bin
RUN curl -L -O "https://github.com/arturo-lang/nightly/releases/download/tag-${TAG}/${ARCHIVE}" && \
    tar -xvf "${ARCHIVE}" arturo && \
    chmod +x arturo && \
    rm "${ARCHIVE}"

FROM alpine:3.20.0

RUN apk add --no-cache jq coreutils

COPY --from=build /root/.arturo/ /root/.arturo/

ENV PATH="/root/.arturo/bin:${PATH}"

WORKDIR /opt/test-runner
COPY bin/run.sh bin/run.sh
ENTRYPOINT ["/opt/test-runner/bin/run.sh"]
