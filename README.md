# Local Spark Cluster with Jupyter Notebooks

This project sets up a local Apache Spark cluster using Docker Compose, with Jupyter Lab for interactive data analysis using PySpark. **Everything is controlled by a centralized configuration file.**

TLDR: make setup, make build, make up

## ✨ Features

- **🎛️ Centralized Configuration**: Control everything from `config/config.yaml`
- **⚡ UV Package Manager**: Fast Python package installation 
- **🔧 Configurable Resources**: Easily adjust memory, cores, and workers
- **📦 Custom Packages**: Add your own Python packages via config
- **🏗️ Easy Management**: Simple commands via Makefile
- **📁 Organized Structure**: Clean folder organization

## Architecture

The setup includes:
- **Spark Master**: Coordinates the cluster and provides the Spark UI
- **Spark Worker**: Executes Spark applications (scalable)
- **Jupyter Lab**: Interactive notebook environment with PySpark

All components use **Spark 3.5.0** to ensure version compatibility.

## Prerequisites

- Docker and Docker Compose installed
- At least 4GB of RAM available for containers
- Python 3.x (for configuration management)

## 🚀 Quick Start

### 1. Configuration

Edit `config/config.yaml` to customize your environment:

```yaml
# Spark Cluster Configuration
spark:
  version: "3.5.0"
  worker:
    memory: "4g"      # Increase worker memory
    cores: "4"        # Increase worker cores
    instances: 2      # Run 2 workers

# Python Package Configuration
python:
  packages:
    - "pandas>=2.0.0"
    - "your-custom-package>=1.0.0"  # Add your packages here
```

### 2. Start the Environment

```bash
# Build and start everything
make up

# Or manually:
docker compose -f docker/docker-compose.yml --env-file config/.env up -d
```

### 3. Access Services
#### A. Via Jupyter Lab
- **Jupyter Lab**: http://localhost:8888 (no password)
- **Spark Master UI**: http://localhost:8080
- **Spark Worker UI**: http://localhost:8081
#### B. Via VSCode
- Open the ipynb file in VSCode
- On the top right corner, click "Select Kernel"
- Select "Kernel > Existing Jupyter Server"
- Enter "http://localhost:8888". Refer to file config/config.yaml under containers > jupyter > port
- Click "Select"
- You can now run the notebook

## 📁 Directory Structure

```
local_spark/
├── config/                    # 🎛️ Configuration files
│   ├── config.yaml           # Centralized configuration (SINGLE SOURCE OF TRUTH)
│   └── .env                  # Environment variables (auto-generated)
├── docker/                   # 🐳 Docker files
│   ├── Dockerfile            # Custom Jupyter image with UV
│   └── docker-compose.yml    # Container orchestration (auto-generated)
├── scripts/                  # 🛠️ Automation scripts
│   └── setup.py              # Configuration generator
├── notebooks/                # 📓 Your Jupyter notebooks
├── data/                     # 📊 Data files
├── Makefile                  # 🎯 Management commands
└── README.md                 # 📖 This file
```

## 🛠️ Management Commands

Use the Makefile for easy management:

```bash
make help          # Show all commands
make setup         # Generate files from config/config.yaml
make up            # Start the cluster
make down          # Stop the cluster
make restart       # Restart everything
make logs          # Show container logs
make status        # Show container status
make clean         # Clean up everything
make rebuild       # Complete rebuild
```

## ⚙️ Configuration

### Python Packages

All Python packages are defined in `config/config.yaml` - **no separate requirements.txt needed!**

```yaml
python:
  packages:
    - "tensorflow>=2.13.0"
    - "torch>=2.0.0"
    - "transformers>=4.30.0"
    - "your-package>=1.0.0"
```

The Dockerfile reads packages directly from `config/config.yaml` during build.

### Spark Resources

Edit `config/config.yaml` to adjust resources:

```yaml
spark:
  worker:
    memory: "4g"      # Worker memory
    cores: "4"        # Worker cores
    instances: 3      # Number of workers
  executor:
    memory: "2g"      # Executor memory per job
    cores: "2"        # Executor cores per job
```

### Scaling Workers

Scale workers dynamically:

```bash
# Using make
make scale-workers

# Or directly with docker compose
docker compose -f docker/docker-compose.yml --env-file config/.env up -d --scale spark-worker=5
```

## 🔧 Advanced Configuration

### Custom Ports

Change ports in `config/config.yaml`:

```yaml
containers:
  jupyter:
    port: 9999
  spark_master:
    ui_port: 9090
    port: 7077
```

### Volume Paths

Customize data and notebook paths:

```yaml
volumes:
  notebooks_path: "./my-notebooks"
  data_path: "./my-data"
```

### Python Version

Change Python version:

```yaml
python:
  version: "3.12"  # Use Python 3.12
```

## 📊 Using Jupyter Notebooks

### Connecting to Spark

In your notebook cells:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("My Spark App") \
    .master("spark://spark-master:7077") \
    .config("spark.executor.memory", "2g") \
    .config("spark.executor.cores", "2") \
    .getOrCreate()
```

### Example Notebook

See the `notebooks/spark_example.ipynb` for examples of:
- Creating Spark sessions
- Loading and manipulating data
- Performing aggregations
- Saving data as Parquet files

## 🔄 Updating Configuration

1. **Edit** `config/config.yaml`
2. **Regenerate** files: `make setup`
3. **Rebuild**: `make rebuild`

## 🚨 Troubleshooting

### Configuration Issues

```bash
make config          # Show current configuration
make logs           # Check container logs
```

### Memory Issues

Reduce memory in `config/config.yaml`:

```yaml
spark:
  worker:
    memory: "1g"
  executor:
    memory: "512m"
```

### Package Installation Issues

Check UV installation:

```bash
docker compose -f docker/docker-compose.yml --env-file config/.env exec jupyter uv --version
```

### Version Compatibility

All containers use versions from `config/config.yaml`. Ensure compatibility:

```yaml
spark:
  version: "3.5.0"
python:
  packages:
    - "pyspark[sql]==3.5.0"  # Match Spark version
```

## 📈 Performance Tips

1. **Scale workers**: Increase `worker.instances` in config
2. **Optimize memory**: Adjust `worker.memory` and `executor.memory`
3. **Partition data**: Use `.repartition()` in your code
4. **Monitor**: Check Spark UI at http://localhost:8080

## 🔒 Production Notes

For production environments:
- Enable Spark security in config
- Use persistent volumes
- Set resource limits
- Configure monitoring
- Use external data sources (S3, HDFS)

## 🆘 Need Help?

1. **Check logs**: `make logs`
2. **Verify config**: `make config`
3. **Clean rebuild**: `make rebuild`
4. **Check resources**: Ensure Docker has enough memory allocated 