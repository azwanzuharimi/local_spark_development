#!/usr/bin/env python3
"""
Setup script for Spark environment configuration.
Reads config/config.yaml and generates necessary files for Docker setup.
"""

import yaml
import os
from pathlib import Path

def load_config():
    """Load configuration from config/config.yaml"""
    config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def generate_env_file(config):
    """Generate .env file for docker-compose in config directory"""
    env_content = f"""# Auto-generated from config/config.yaml
# Spark Configuration
SPARK_VERSION={config['spark']['version']}
SPARK_MASTER_MEMORY={config['spark']['master']['memory']}
SPARK_MASTER_CORES={config['spark']['master']['cores']}
SPARK_WORKER_MEMORY={config['spark']['worker']['memory']}
SPARK_WORKER_CORES={config['spark']['worker']['cores']}
SPARK_WORKER_INSTANCES={config['spark']['worker']['instances']}
SPARK_EXECUTOR_MEMORY={config['spark']['executor']['memory']}
SPARK_EXECUTOR_CORES={config['spark']['executor']['cores']}

# Python Configuration
PYTHON_VERSION={config['python']['version']}

# Container Ports
JUPYTER_PORT={config['containers']['jupyter']['port']}
SPARK_MASTER_UI_PORT={config['containers']['spark_master']['ui_port']}
SPARK_MASTER_PORT={config['containers']['spark_master']['port']}
SPARK_WORKER_UI_PORT={config['containers']['spark_worker']['ui_port']}

# Volume Paths
NOTEBOOKS_PATH={config['volumes']['notebooks_path']}
DATA_PATH={config['volumes']['data_path']}

# Network
NETWORK_NAME={config['network']['name']}
"""
    
    config_dir = Path(__file__).parent.parent / 'config'
    with open(config_dir / '.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Generated config/.env file")

def generate_docker_compose(config):
    """Generate docker-compose.yml from config in docker directory"""
    network_name = config['network']['name']
    compose_content = f'''# Configuration-driven Spark environment
services:
  spark-master:
    image: bitnami/spark:${{SPARK_VERSION:-3.5.0}}
    container_name: spark-master
    environment:
      - SPARK_MODE=master
      - SPARK_RPC_AUTHENTICATION_ENABLED=no
      - SPARK_RPC_ENCRYPTION_ENABLED=no
      - SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED=no
      - SPARK_SSL_ENABLED=no
      - SPARK_USER=spark
    ports:
      - "${{SPARK_MASTER_UI_PORT:-8080}}:8080"
      - "${{SPARK_MASTER_PORT:-7077}}:7077"
    volumes:
      - ../${{NOTEBOOKS_PATH:-./notebooks}}:/opt/notebooks
      - ../${{DATA_PATH:-./data}}:/opt/data
      - ../${{DATA_PATH:-./data}}:/home/jovyan/data
    networks:
      - {network_name}

  spark-worker:
    image: bitnami/spark:${{SPARK_VERSION:-3.5.0}}
    container_name: spark-worker
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
      - SPARK_WORKER_MEMORY=${{SPARK_WORKER_MEMORY:-2g}}
      - SPARK_WORKER_CORES=${{SPARK_WORKER_CORES:-2}}
      - SPARK_RPC_AUTHENTICATION_ENABLED=no
      - SPARK_RPC_ENCRYPTION_ENABLED=no
      - SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED=no
      - SPARK_SSL_ENABLED=no
      - SPARK_USER=spark
    ports:
      - "${{SPARK_WORKER_UI_PORT:-8081}}:8081"
    volumes:
      - ../${{NOTEBOOKS_PATH:-./notebooks}}:/opt/notebooks
      - ../${{DATA_PATH:-./data}}:/opt/data
      - ../${{DATA_PATH:-./data}}:/home/jovyan/data
    depends_on:
      - spark-master
    networks:
      - {network_name}
    deploy:
      replicas: ${{SPARK_WORKER_INSTANCES:-1}}

  jupyter:
    build: 
      context: ..
      dockerfile: docker/Dockerfile
      args:
        PYTHON_VERSION: ${{PYTHON_VERSION:-3.11}}
    container_name: jupyter-pyspark
    environment:
      - JUPYTER_ENABLE_LAB=yes
      - SPARK_MASTER_URL=spark://spark-master:7077
      - PYSPARK_SUBMIT_ARGS=--master spark://spark-master:7077 --executor-memory ${{SPARK_EXECUTOR_MEMORY:-1g}} --executor-cores ${{SPARK_EXECUTOR_CORES:-1}} pyspark-shell
    ports:
      - "${{JUPYTER_PORT:-8888}}:8888"
    volumes:
      - ../${{NOTEBOOKS_PATH:-./notebooks}}:/home/jovyan/notebooks
      - ../${{DATA_PATH:-./data}}:/home/jovyan/data
      - ../${{DATA_PATH:-./data}}:/opt/data
    depends_on:
      - spark-master
      - spark-worker
    networks:
      - {network_name}

networks:
  {network_name}:
    driver: bridge

volumes:
  notebooks:
  data:
'''
    
    docker_dir = Path(__file__).parent.parent / 'docker'
    with open(docker_dir / 'docker-compose.yml', 'w') as f:
        f.write(compose_content)
    
    print("✅ Generated docker/docker-compose.yml")

def create_directories(config):
    """Create necessary directories"""
    base_dir = Path(__file__).parent.parent
    notebooks_path = base_dir / config['volumes']['notebooks_path'].lstrip('./')
    data_path = base_dir / config['volumes']['data_path'].lstrip('./')
    
    notebooks_path.mkdir(exist_ok=True)
    data_path.mkdir(exist_ok=True)
    
    print(f"✅ Created directories: {notebooks_path.name}, {data_path.name}")

def main():
    """Main setup function"""
    print("🚀 Setting up Spark environment from config/config.yaml...")
    
    try:
        config = load_config()
        print("✅ Loaded config/config.yaml")
        
        # Generate files from config
        generate_env_file(config)
        generate_docker_compose(config)
        create_directories(config)
        
        print("\n🎉 Setup complete! Run the following commands:")
        print("1. docker compose -f docker/docker-compose.yml --env-file config/.env up -d")
        print("2. Open http://localhost:8888 for Jupyter Lab")
        print("3. Open http://localhost:8080 for Spark Master UI")
        
        print("\n📝 To modify configuration:")
        print("1. Edit config/config.yaml")
        print("2. Run: python scripts/setup.py")
        print("3. Run: docker compose -f docker/docker-compose.yml --env-file config/.env up -d --build")
        
        print("\n📦 Python packages are read directly from config/config.yaml - no requirements.txt needed!")
        
    except FileNotFoundError:
        print("❌ config/config.yaml not found! Please create it first.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 