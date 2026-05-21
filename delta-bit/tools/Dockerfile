FROM antsx/ants:master

WORKDIR /python_env
RUN chmod 777 /python_env

RUN apt-get update && \
    apt-get install -y \
    dcm2niix \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Make a virtual environment
RUN python3 -m venv /python_env/venv

# Update pip inside venv and install libraries
RUN /python_env/venv/bin/pip install --upgrade pip && \
    /python_env/venv/bin/pip install --no-cache-dir fastapi uvicorn

# Set venv as default for the container
ENV PATH="/python_env/venv/bin:$PATH"

WORKDIR /data

CMD ["uvicorn", "script.reg_mni:app", "--host", "0.0.0.0", "--port", "8000"]