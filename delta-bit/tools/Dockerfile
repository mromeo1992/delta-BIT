FROM antsx/ants:master

WORKDIR /data


RUN apt-get update && \
    apt-get install -y \
    dcm2niix \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install fastapi uvicorn

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]