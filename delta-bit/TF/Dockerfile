# Dockerfile
FROM tensorflow/tensorflow:2.10.0-gpu

# Evita prompt interattivi
ENV DEBIAN_FRONTEND=noninteractive

# Aggiorna e installa dipendenze di sistema minime
RUN apt-get update && apt-get install -y \
    #git \
    build-essential \
    #wget \
    #unzip \
    ca-certificates \
    #libglib2.0-0 \
    #libsm6 \
    #libxext6 \
    #libxrender-dev \
    #pigz \
    #gzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia requirements e installa
COPY requirements.txt .
RUN pip install --no-cache-dir --use-feature=2020-resolver -r requirements.txt

WORKDIR /app/data


# Comando di avvio: lancia Streamlit
#CMD ["streamlit", "run", "app/streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
#CMD ["/bin/bash"]
CMD ["uvicorn", "script.tf_open_port:app2", "--host", "0.0.0.0", "--port", "9000"]
