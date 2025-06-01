# Configuration-driven Dockerfile
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

# Install system dependencies including PyYAML for config reading
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    procps \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv pyyaml

# Copy configuration file from config directory
COPY config/config.yaml /tmp/config.yaml

# Install Python packages from config as root (has permission to install system-wide)
RUN echo '#!/usr/bin/env python3\n\
import yaml\n\
import subprocess\n\
import sys\n\
\n\
with open("/tmp/config.yaml", "r") as f:\n\
    config = yaml.safe_load(f)\n\
\n\
packages = config["python"]["packages"]\n\
for package in packages:\n\
    subprocess.run([sys.executable, "-m", "uv", "pip", "install", "--system", package], check=True)\n\
' > /tmp/install_packages.py && \
    python3 /tmp/install_packages.py && \
    rm /tmp/install_packages.py /tmp/config.yaml

# Create user
RUN useradd -m -s /bin/bash jovyan
USER jovyan
WORKDIR /home/jovyan

# Set up environment
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=jupyter
ENV JUPYTER_ENABLE_LAB=yes

# Create directories
RUN mkdir -p /home/jovyan/notebooks /home/jovyan/data

WORKDIR /home/jovyan

EXPOSE 8888 4040

# Start Jupyter Lab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=", "--NotebookApp.password="] 