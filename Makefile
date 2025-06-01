# Spark Environment Management
.PHONY: help setup build up down restart logs clean status scale-workers

# Docker compose command with correct paths
COMPOSE_CMD = docker compose -f docker/docker-compose.yml --env-file config/.env

# Default target
help:
	@echo "🚀 Spark Environment Commands"
	@echo ""
	@echo "Configuration:"
	@echo "  setup     - Generate all files from config/config.yaml"
	@echo "  config    - Show current configuration"
	@echo ""
	@echo "Environment:"
	@echo "  build     - Build the Jupyter container with UV"
	@echo "  up        - Start the Spark cluster"
	@echo "  down      - Stop the Spark cluster"
	@echo "  restart   - Restart the entire cluster"
	@echo ""
	@echo "Monitoring:"
	@echo "  logs      - Show container logs"
	@echo "  status    - Show container status"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean     - Clean up containers and images"
	@echo "  rebuild   - Clean rebuild of everything"
	@echo ""
	@echo "📦 Python packages are managed directly in config/config.yaml"
	@echo ""
	@echo "Access URLs:"
	@echo "  - Jupyter Lab: http://localhost:8888"
	@echo "  - Spark Master UI: http://localhost:8080"
	@echo "  - Spark Worker UI: http://localhost:8081"

# Generate configuration files from config/config.yaml
setup:
	@echo "🔧 Generating configuration files..."
	@python3 scripts/setup.py || echo "⚠️  Install pyyaml to use automated setup: pip3 install pyyaml"

# Show current configuration
config:
	@echo "📋 Current Configuration:"
	@cat config/.env 2>/dev/null || echo "⚠️  config/.env file not found. Run 'make setup' first."

# Build the custom Jupyter container
build:
	@echo "🏗️  Building Jupyter container with UV..."
	$(COMPOSE_CMD) build jupyter

# Start the environment
up:
	@echo "🚀 Starting Spark cluster..."
	$(COMPOSE_CMD) up -d
	@echo ""
	@echo "✅ Cluster started!"
	@echo "   📊 Jupyter Lab: http://localhost:8888"
	@echo "   🎯 Spark Master: http://localhost:8080"
	@echo "   ⚡ Spark Worker: http://localhost:8081"

# Stop the environment
down:
	@echo "🛑 Stopping Spark cluster..."
	$(COMPOSE_CMD) down

# Restart everything
restart: down up

# Show container logs
logs:
	@echo "📋 Container Logs:"
	$(COMPOSE_CMD) logs -f

# Show container status
status:
	@echo "📊 Container Status:"
	$(COMPOSE_CMD) ps

# Clean up everything
clean:
	@echo "🧹 Cleaning up..."
	$(COMPOSE_CMD) down -v
	docker system prune -f
	@echo "✅ Cleanup complete!"

# Complete rebuild
rebuild: clean build up

# Scale workers
scale-workers:
	@echo "⚡ Scaling Spark workers..."
	@read -p "Number of workers: " workers; \
	$(COMPOSE_CMD) up -d --scale spark-worker=$$workers 