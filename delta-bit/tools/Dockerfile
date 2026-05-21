FROM antsx/ants:master

WORKDIR /data


RUN apt-get update && \
    apt-get install -y \
    dcm2niix \
    && rm -rf /var/lib/apt/lists/*


