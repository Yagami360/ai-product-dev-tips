# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a comprehensive AI product development tips repository containing practical examples and code snippets for various AI/ML development tasks. The repository is structured as a collection of numbered examples across different domains, with extensive documentation in Japanese.

## Key Directory Structure

- **ml_ops/**: MLOps and machine learning operations (119+ examples)
- **front_end/**: Frontend development including web apps, mobile apps, and cross-platform development
- **image_processing/**: Computer vision and image processing utilities
- **nlp_processing/**: Natural language processing and LLM integration examples
- **server_processing/**: Server deployment, APIs, and infrastructure
- **pytorch_tips/**: PyTorch-specific examples and best practices
- **acceleration_processing/**: Performance optimization techniques
- **docker_processing/**: Docker containerization examples
- **conda_processing/**: Conda environment management
- **io_processing/**: File I/O and data processing utilities

## Common Development Commands

### Code Quality and Formatting
```bash
# Lint code (available in some projects)
make lint
flake8 .

# Format code (available in some projects) 
make fmt
black .
isort -rc -sl .
isort -rc -m 3 .

# Check formatting
make check-fmt
isort -rc -m 3 --check-only .
```

### Docker Operations
```bash
# Most projects use docker-compose for local development
docker-compose up -d
docker-compose down
docker-compose -f docker-compose.yml up -d

# Many examples include specific run scripts
./run_api_local.sh
./run_api_dev.sh
```

### Common Script Patterns
```bash
# API testing
python request.py --host 0.0.0.0 --port 5000
./run_request.sh

# GKE deployment (in applicable examples)
./deploy_api_gke.sh
./run_gke.sh

# Firebase deployment
./deploy_webapp_firebase.sh
./deploy_webapp_firebase_hosting.sh
```

## Architecture Patterns

### Multi-Service ML Applications
Many examples follow a microservices pattern with:
- **predict-server**: ML inference service
- **redis-server**: Caching layer for model results
- **batch-server**: Batch processing for training jobs
- **proxy-server**: Nginx load balancing
- **monitoring-server**: Observability and metrics

### Container-First Development
- All examples use Docker for reproducible environments
- GPU support available through nvidia/cuda base images
- Multi-stage builds for production optimization

### Cloud-Native Deployment
- Heavy emphasis on Google Cloud Platform (GKE, Cloud Functions, Firebase)
- AWS examples for EKS, Lambda, and other services
- Kubernetes manifests for production deployments

## Technology Stack Patterns

### Python ML/AI Projects
- **Core ML**: PyTorch, TensorFlow, Transformers (Hugging Face)
- **APIs**: Flask, FastAPI, Uvicorn
- **Data**: pandas, numpy, OpenCV, Pillow
- **Quality**: black, flake8, isort, pytest
- **ML Pipeline**: Kedro for structured ML workflows

### JavaScript/Node.js Projects
- **Frontend**: React, Vue.js, Next.js
- **Backend**: Express.js, Firebase Functions
- **Mobile**: Flutter for cross-platform development

### Infrastructure
- **Containerization**: Docker, docker-compose
- **Orchestration**: Kubernetes, Docker Swarm
- **CI/CD**: GitHub Actions, Cloud Build
- **Monitoring**: Grafana, Prometheus, custom exporters

## Development Workflow

### For New Examples
1. Create numbered directory (e.g., `ml_ops/120/`)
2. Include `README.md` with Japanese documentation
3. Add `requirements.txt` or `package.json` as needed
4. Create shell scripts for common operations (`run_*.sh`, `deploy_*.sh`)
5. Include `docker-compose.yml` for local development
6. Add request/test scripts for APIs

### For Testing Examples
```bash
# Navigate to specific example
cd ml_ops/108/

# Run local development
./run_api_dev.sh

# Test the implementation
python request.py
```

## Important Notes

- Documentation is primarily in Japanese
- Examples are self-contained within their numbered directories
- Many examples include both local development and cloud deployment options
- Shell scripts use `set -eu` for proper error handling
- GPU support is available in ML/NLP examples through CUDA base images
- All API examples include request/testing scripts

## File Naming Conventions

- `README.md`: Japanese documentation for each example
- `run_*.sh`: Local development execution scripts
- `deploy_*.sh`: Deployment scripts for cloud platforms
- `request.py`: API testing and interaction scripts
- `docker-compose.yml`: Local multi-service setup
- `cloudbuild.yml`: Google Cloud Build configuration
- `Dockerfile`: Container definitions

When working with this repository, focus on the self-contained nature of each example and leverage the existing patterns for consistency.