# AnythingLLM - Deployment Infrastructure

## Purpose
This document covers the deployment infrastructure and containerization strategies for AnythingLLM, including Docker containers, cloud platform deployments, and Kubernetes orchestration.

## Technologies Used
- **Docker**: Containerization with multi-stage builds
- **Docker Compose**: Local development orchestration
- **AWS CloudFormation**: Infrastructure as Code for AWS
- **Google Cloud Deployment Manager**: GCP infrastructure automation
- **Terraform**: DigitalOcean infrastructure provisioning
- **Kubernetes**: Container orchestration and scaling
- **Ubuntu 22.04**: Base container operating system

## Architecture Overview

### Deployment Strategy
AnythingLLM supports multiple deployment patterns:

1. **Single Container**: All services (server, collector, frontend) in one container
2. **Cloud Platform**: One-click deployments on AWS, GCP, DigitalOcean
3. **Kubernetes**: Scalable container orchestration
4. **Bare Metal**: Direct installation without containers

## Docker Implementation

### Multi-Stage Dockerfile Architecture
```dockerfile
# Multi-architecture support
FROM ubuntu:jammy-20240627.1 AS base

# Architecture-specific stages
FROM base AS build-arm64
# ARM64-specific Chromium installation for Puppeteer
RUN curl https://playwright.azureedge.net/builds/chromium/1088/chromium-linux-arm64.zip -o chrome-linux.zip && \
    unzip chrome-linux.zip && \
    rm -rf chrome-linux.zip

FROM base AS build-amd64
# AMD64 uses standard Puppeteer Chromium

# Common build flow
FROM build-${TARGETARCH} AS build
# System dependencies and Node.js installation

# Frontend build stage
FROM build AS frontend-build
COPY --chown=anythingllm:anythingllm ./frontend /app/frontend/
RUN yarn install && yarn build

# Backend build stage  
FROM build AS backend-build
COPY --chown=anythingllm:anythingllm ./server /app/server/
COPY --chown=anythingllm:anythingllm ./collector/ ./collector/
RUN yarn install --production

# Production assembly
FROM backend-build AS production-build
COPY --from=frontend-build /app/frontend/dist /app/server/public
```

**Key Design Decisions**:

#### 1. **Multi-Architecture Support**
```dockerfile
# Conditional architecture-specific builds
FROM build-${TARGETARCH} AS build
```
**Rationale**: Supports both ARM64 (Apple Silicon, ARM servers) and AMD64 architectures with optimized binaries

#### 2. **ARM64 Chromium Patching**
```dockerfile
# ARM64-specific Puppeteer fix
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV CHROME_PATH=/app/chrome-linux/chrome
ENV PUPPETEER_EXECUTABLE_PATH=/app/chrome-linux/chrome
```
**Rationale**: Puppeteer doesn't ship ARM64-compatible Chromium, requiring manual installation

#### 3. **Security-First Container Design**
```dockerfile
# Non-root user creation
ARG ARG_UID=1000
ARG ARG_GID=1000
RUN groupadd -g "$ARG_GID" anythingllm && \
    useradd -l -u "$ARG_UID" -m -d /app -s /bin/bash -g anythingllm anythingllm

USER anythingllm
```
**Rationale**: Runs as non-root user with configurable UID/GID for host compatibility

#### 4. **Multi-Service Orchestration**
```bash
# docker-entrypoint.sh - Process management
{
  cd /app/server/ &&
    npx prisma generate &&
    npx prisma migrate deploy &&
    node /app/server/index.js
} &
{ node /app/collector/index.js; } &
wait -n  # Wait for any process to exit
exit $?
```
**Rationale**: Runs both server and collector services in parallel within single container

### Docker Compose Development Setup
```yaml
# docker-compose.yml
services:
  anything-llm:
    build:
      context: ../.
      dockerfile: ./docker/Dockerfile
      args:
        ARG_UID: ${UID:-1000}
        ARG_GID: ${GID:-1000}
    cap_add:
      - SYS_ADMIN  # Required for Puppeteer/Chromium
    volumes:
      - "./.env:/app/server/.env"
      - "../server/storage:/app/server/storage"
      - "../collector/hotdir/:/app/collector/hotdir"
      - "../collector/outputs/:/app/collector/outputs"
    ports:
      - "3001:3001"
    networks:
      - anything-llm
```

**Features**:
- **Volume persistence**: Database and file storage persistence
- **Environment configuration**: External .env file mounting
- **Network isolation**: Dedicated bridge network
- **Capability management**: SYS_ADMIN for browser automation

## Cloud Platform Deployments

### AWS CloudFormation Template
```json
{
  "AWSTemplateFormatVersion": "2010-09-09",
  "Description": "Create a stack that runs AnythingLLM on a single instance",
  "Parameters": {
    "InstanceType": {
      "Type": "String",
      "Default": "t3.small"
    },
    "InstanceVolume": {
      "Type": "Number",
      "Default": 10,
      "MinValue": 4
    }
  },
  "Resources": {
    "AnythingLLMInstance": {
      "Type": "AWS::EC2::Instance",
      "Properties": {
        "ImageId": { "Fn::FindInMap": ["Region2AMI", {"Ref": "AWS::Region"}, "AMI"] },
        "InstanceType": { "Ref": "InstanceType" },
        "SecurityGroupIds": [{ "Ref": "AnythingLLMInstanceSecurityGroup" }],
        "UserData": {
          "Fn::Base64": {
            "Fn::Join": ["", [
              "#!/bin/bash\n",
              "sudo docker pull mintplexlabs/anythingllm\n",
              "sudo docker run -d -p 3001:3001 --cap-add SYS_ADMIN mintplexlabs/anythingllm\n"
            ]]
          }
        }
      }
    }
  }
}
```

**AWS Deployment Features**:
- **Auto-scaling groups**: Optional horizontal scaling
- **Load balancer integration**: Application Load Balancer support
- **EBS volume management**: Persistent storage configuration
- **Security groups**: Automated firewall rules
- **Multi-region support**: Region-specific AMI mapping

### Google Cloud Platform Deployment
```yaml
# gcp_deploy_anything_llm.yaml
resources:  
  - name: anything-llm-instance  
    type: compute.v1.instance  
    properties:  
      zone: us-central1-a  
      machineType: zones/us-central1-a/machineTypes/n1-standard-1  
      disks:  
        - deviceName: boot  
          type: PERSISTENT  
          boot: true  
          initializeParams:  
            sourceImage: projects/ubuntu-os-cloud/global/images/family/ubuntu-2004-lts  
            diskSizeGb: 10  
      metadata:  
        items:  
          - key: startup-script  
            value: |  
              #!/bin/bash  
              sudo apt-get update  
              sudo apt-get install -y docker.io  
              sudo docker pull mintplexlabs/anythingllm
              sudo docker run -d -p 3001:3001 --cap-add SYS_ADMIN mintplexlabs/anythingllm
```

**GCP Features**:
- **Compute Engine**: VM-based deployment
- **Persistent disks**: Automatic storage attachment
- **Startup scripts**: Automated Docker installation and container launch
- **Network configuration**: Default VPC with external IP

### DigitalOcean Terraform Configuration
```hcl
# main.tf
resource "digitalocean_droplet" "anythingllm" {
  image     = "ubuntu-22-04-x64"
  name      = "anythingllm-droplet"
  region    = var.region
  size      = var.droplet_size
  user_data = file("user_data.tpl")

  tags = ["anythingllm"]
}

resource "digitalocean_firewall" "anythingllm" {
  name = "anythingllm-firewall"
  
  droplet_ids = [digitalocean_droplet.anythingllm.id]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "3001"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }
}
```

**DigitalOcean Features**:
- **Infrastructure as Code**: Terraform-managed resources
- **Firewall automation**: Automated security rule creation
- **Flexible sizing**: Configurable droplet sizes
- **User data scripts**: Automated setup on first boot

## Kubernetes Deployment

### Kubernetes Manifest Structure
```yaml
# manifest.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: anything-llm-volume
spec:
  storageClassName: gp2
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  awsElasticBlockStore:
    volumeID: "{{ anythingllm_awsElasticBlockStore_volumeID }}"
    fsType: ext4

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: anything-llm
spec:
  replicas: 1
  selector:
    matchLabels:
      k8s-app: anything-llm
  template:
    spec:
      containers:
      - name: anything-llm
        image: mintplexlabs/anythingllm:latest
        ports:
        - containerPort: 3001
        securityContext:
          capabilities:
            add:
            - SYS_ADMIN
        volumeMounts:
        - name: anything-llm-storage
          mountPath: /app/server/storage
        env:
        - name: STORAGE_DIR
          value: "/app/server/storage"
      volumes:
      - name: anything-llm-storage
        persistentVolumeClaim:
          claimName: anything-llm-volume-claim

---
apiVersion: v1
kind: Service
metadata:
  name: anything-llm-service
spec:
  selector:
    k8s-app: anything-llm
  ports:
  - port: 3001
    targetPort: 3001
  type: LoadBalancer
```

**Kubernetes Features**:
- **Persistent storage**: EBS volume integration
- **Service discovery**: Kubernetes service networking
- **Load balancing**: External load balancer provisioning
- **Security contexts**: Container capability management
- **Horizontal scaling**: Replica management (single replica for database consistency)

## Container Health and Monitoring

### Health Check Implementation
```bash
# docker-healthcheck.sh
#!/bin/bash

# Check if server is responding
curl -f http://localhost:3001/api/ping >/dev/null 2>&1
server_status=$?

# Check if collector is responding  
curl -f http://localhost:8888/accepts >/dev/null 2>&1
collector_status=$?

if [ $server_status -eq 0 ] && [ $collector_status -eq 0 ]; then
    echo "Both services are healthy"
    exit 0
else
    echo "Health check failed - server: $server_status, collector: $collector_status"
    exit 1
fi
```

```dockerfile
# Dockerfile health check configuration
HEALTHCHECK --interval=1m --timeout=10s --start-period=1m \
  CMD /bin/bash /usr/local/bin/docker-healthcheck.sh || exit 1
```

**Monitoring Features**:
- **Multi-service health**: Checks both server and collector endpoints
- **Configurable intervals**: 1-minute health check intervals
- **Startup grace period**: 1-minute startup time allowance
- **Container orchestration**: Integration with Docker/Kubernetes health systems

## Specialized Deployments

### Hugging Face Spaces
```dockerfile
# huggingface-spaces/Dockerfile
FROM mintplexlabs/anythingllm:latest
EXPOSE 7860
ENV ANYTHING_LLM_RUNTIME=huggingface
```
**Features**: Optimized for Hugging Face Spaces platform with port 7860 exposure

### Development vs Production
```bash
# Development override in docker-entrypoint.sh
if [ "$NODE_ENV" = "development" ]; then
    echo "Running in development mode"
    # Additional development-specific setup
fi

# Production optimizations
ENV NODE_ENV=production
ENV ANYTHING_LLM_RUNTIME=docker
ENV DEPLOYMENT_VERSION=1.8.4
```

## Notable Technical Decisions

### 1. **Single Container Strategy**
**Decision**: All services in one container vs. microservice containers
**Rationale**: 
- Simplifies deployment for end users
- Reduces networking complexity
- Maintains service coupling for database consistency
- Easier resource management and monitoring

### 2. **Multi-Architecture Docker Images**
**Decision**: Support both ARM64 and AMD64 in single image
**Rationale**:
- Apple Silicon Mac compatibility
- ARM-based cloud instances (AWS Graviton)
- Cost optimization opportunities

### 3. **Puppeteer/Chromium Handling**
**Decision**: Manual Chromium installation for ARM64
**Rationale**:
- Puppeteer doesn't provide ARM64 Chromium binaries
- Web scraping functionality critical for document collection
- Better than disabling web scraping entirely

### 4. **Database Migration Strategy**
```bash
# Automatic migrations on container start
npx prisma generate --schema=./prisma/schema.prisma &&
npx prisma migrate deploy --schema=./prisma/schema.prisma
```
**Rationale**: Ensures database schema consistency across deployments without manual intervention

### 5. **Storage Volume Strategy**
**Decision**: External volume mounting for persistence
**Rationale**:
- Data persistence across container restarts
- Backup and migration capabilities
- Separation of application and data layers

This deployment infrastructure enables AnythingLLM to run reliably across various environments from local development to enterprise cloud deployments, with consistent behavior and easy scalability options.