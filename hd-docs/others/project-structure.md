# AnythingLLM - Project Structure

## Purpose
This document provides an overview of the AnythingLLM monorepo structure, a full-stack LLM-based application for turning private documents into an intelligent chat interface.

## Technologies Used
- **Node.js**: Runtime environment (>= 18.12.1)
- **JavaScript**: Primary programming language
- **Yarn**: Package management and script orchestration
- **Express.js**: Web framework for backend services
- **React + Vite**: Frontend framework and build tool
- **Prisma**: Database ORM and migrations
- **Docker**: Containerization and deployment

## Architecture Overview

AnythingLLM follows a **microservices-like monorepo architecture** with three main application components:

### Core Components

1. **`server/`** - Main backend API server
   - Express.js application serving REST APIs
   - Handles LLM interactions, vector database management
   - User authentication and workspace management
   - WebSocket support for real-time features

2. **`collector/`** - Document processing service  
   - Dedicated Express.js server for document ingestion
   - Handles file parsing, web scraping, and text extraction
   - Runs on port 8888 independently from main server

3. **`frontend/`** - React-based user interface
   - Vite-powered development and build system
   - Tailwind CSS for styling
   - Multi-language support via i18next

### Supporting Infrastructure

4. **`cloud-deployments/`** - Cloud deployment configurations
   - AWS CloudFormation templates
   - Google Cloud Platform deployment scripts
   - DigitalOcean Terraform configurations
   - Kubernetes manifests

5. **`docker/`** - Containerization setup
   - Multi-stage Dockerfile
   - Docker Compose orchestration
   - Health check scripts

6. **`extras/`** - Additional utilities and scripts
   - Support tools and helper scripts
   - Announcement and documentation assets

## Key Technical Decisions

### Monorepo Structure
- **Rationale**: Enables coordinated development across frontend, backend, and collector services
- **Implementation**: Yarn workspaces with centralized script management in root `package.json`
- **Benefits**: Simplified dependency management, consistent tooling, unified build process

### Microservice Architecture
- **Service Separation**: Document processing isolated from main API server for:
  - Resource isolation (document processing can be CPU/memory intensive)
  - Independent scaling capabilities
  - Fault tolerance (document processing failures don't affect main app)

### Development Workflow
```bash
# Unified setup command
yarn setup  # Sets up all environments and dependencies

# Parallel development servers
yarn dev:all  # Runs all three services concurrently
```

### Database Strategy
- **Prisma ORM**: Type-safe database access with automatic migrations
- **SQLite**: Default database for simplicity (production supports PostgreSQL, MySQL)
- **Migration Management**: Automated via `yarn prisma:setup`

## Environment Configuration

The project uses environment-specific configuration:

```javascript
// Dynamic environment loading
process.env.NODE_ENV === "development"
  ? require("dotenv").config({ path: `.env.${process.env.NODE_ENV}` })
  : require("dotenv").config();
```

### Environment Files
- `frontend/.env` - Frontend configuration
- `server/.env.development` - Development server config  
- `collector/.env` - Document collector config
- `docker/.env` - Docker deployment config

## Build and Deployment

### Development Mode
- Hot reloading enabled for all services
- Debug logging and development-specific endpoints
- CORS enabled for cross-origin requests

### Production Mode
- Static asset serving from `server/public/`
- Meta tag generation for SEO
- Security headers (X-Frame-Options: DENY)
- Robots.txt disallowing all crawlers

## Notable Implementation Details

### File Size Handling
- **3GB file limit** across all services
- Configured in both server and collector for large document processing

### Security Measures
- Request body integrity verification in collector
- Path traversal protection with `path.normalize()`
- CORS configuration for controlled access

### WebSocket Integration
- Conditional WebSocket loading based on HTTPS configuration
- Real-time features for chat and agent interactions

This modular architecture enables AnythingLLM to handle complex document processing workflows while maintaining a clean separation of concerns and supporting various deployment scenarios from local development to enterprise cloud deployments.