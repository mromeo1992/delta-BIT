# Dockerfile
FROM tensorflow/tensorflow:2.10.0-gpu

# Evita prompt interattivi
ENV DEBIAN_FRONTEND=noninteractive

# Aggiorna e installa dipendenze di sistema minime
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Crea directory app
WORKDIR /app

# Copia requirements e installa
COPY requirements.txt .
RUN pip install --no-cache-dir --use-feature=2020-resolver -r requirements.txt

# Copia il codice
COPY app/ ./app/

# Imposta la working dir dell'app
WORKDIR /app

# Streamlit: disabilita il controllo di browser headless
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Espone la porta di Streamlit
EXPOSE 8501

# Comando di avvio: lancia Streamlit
CMD ["streamlit", "run", "app/streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
#CMD ["/bin/bash"]
