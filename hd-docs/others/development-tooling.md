# AnythingLLM - Development Tooling & Configuration

## Purpose
This document covers the development tooling, code quality standards, and project maintenance utilities that support the AnythingLLM development workflow.

## Technologies Used
- **ESLint**: JavaScript/JSX linting and code quality
- **Prettier**: Code formatting and style consistency  
- **Hermes**: JavaScript parser for ESLint
- **Yarn**: Package management and script execution
- **Node.js**: Runtime environment and tooling platform

## Code Quality & Standards

### ESLint Configuration
The project uses a comprehensive ESLint setup with multiple configurations for different file types:

```javascript
// eslint.config.js - Modern ESLint flat config
export default [
  eslintRecommended.configs.recommended,
  eslintConfigPrettier,
  {
    languageOptions: {
      parser: hermesParser,        // Facebook's Hermes parser
      parserOptions: {
        ecmaFeatures: { jsx: true }
      },
      ecmaVersion: 2020,
      sourceType: "module",
      globals: {
        ...globals.browser,
        ...globals.es2020,
        ...globals.node
      }
    },
    plugins: {
      ftFlow,                     // Flow type checking
      react,                      // React-specific rules
      "react-hooks": reactHooks,  // React Hooks rules
      prettier                    // Prettier integration
    },
    rules: {
      "no-unused-vars": "warn",
      "no-undef": "warn", 
      "prettier/prettier": "warn"
    }
  }
]
```

#### File-Specific Configurations

**Frontend JSX Files**:
```javascript
{
  files: ["frontend/src/**/*.jsx"],
  plugins: {
    react,
    "jsx-runtime": jsxRuntime,
    "react-hooks": reactHooks,
    "react-refresh": reactRefresh,
    prettier
  },
  rules: {
    ...jsxRuntime.rules,
    "react/prop-types": "off",  // Disabled for development speed
    "react-refresh/only-export-components": "warn"
  }
}
```

**Backend Server Files**:
```javascript
{
  files: [
    "server/endpoints/**/*.js",
    "server/models/**/*.js", 
    "server/utils/**/*.js"
  ],
  rules: {
    "no-undef": "warn"  // Relaxed for Node.js globals
  }
}
```

**Key Decisions**:
- **Hermes Parser**: Facebook's parser for better JSX and modern JS support
- **Warning-level rules**: Non-blocking development with visible feedback
- **Prettier integration**: Automated formatting with ESLint enforcement
- **React 18 targeting**: Optimized for React 18 features and patterns

### Package Management Strategy

#### Unified Dependency Management
```json
// Root package.json - Orchestration scripts
{
  "scripts": {
    "lint": "cd server && yarn lint && cd ../frontend && yarn lint && cd ../collector && yarn lint",
    "setup": "cd server && yarn && cd ../collector && yarn && cd ../frontend && yarn && yarn setup:envs && yarn prisma:setup",
    "dev:all": "npx concurrently \"yarn dev:server\" \"yarn dev:frontend\" \"yarn dev:collector\""
  }
}
```

**Features**:
- **Monorepo coordination**: Single command to manage all services
- **Parallel execution**: Concurrent development servers
- **Environment setup**: Automated .env file creation
- **Database initialization**: Automated Prisma setup

#### Service-Specific Dependencies

**Server Dependencies** (Production-focused):
```json
{
  "dependencies": {
    "@prisma/client": "5.3.1",
    "express": "^5.1.0", 
    "bcrypt": "^5.1.0",
    "jsonwebtoken": "^9.0.0",
    "winston": "^3.13.0"
  }
}
```

**Frontend Dependencies** (UI-focused):
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-router-dom": "^6.3.0",
    "i18next": "^23.11.3",
    "@phosphor-icons/react": "^2.1.7"
  }
}
```

**Collector Dependencies** (Processing-focused):
```json
{
  "dependencies": {
    "puppeteer": "~21.5.2",
    "tesseract.js": "^6.0.0",
    "pdf-parse": "^1.1.1",
    "mammoth": "^1.6.0"
  }
}
```

## Development Utilities

### Version Verification Script
```javascript
// extras/scripts/verifyPackageVersions.mjs
// Ensures version consistency across all package.json files
import fs from 'fs';
import path from 'path';

const packagePaths = [
  './package.json',
  './server/package.json', 
  './frontend/package.json',
  './collector/package.json'
];

// Verify all packages have matching versions
packagePaths.forEach(pkgPath => {
  const pkg = JSON.parse(fs.readFileSync(pkgPath));
  console.log(`${pkgPath}: ${pkg.version}`);
});
```

**Purpose**: Ensures version consistency across the monorepo for releases

### Bare Metal Deployment Guide
The project includes comprehensive bare-metal deployment instructions:

```markdown
# BARE_METAL.md - Production deployment without Docker

## Minimum Requirements
- NodeJS v18
- Yarn
- 2GB RAM minimum
- 10GB disk storage minimum

## Setup Process
1. Clone repository
2. Run `yarn setup` for dependency installation
3. Configure environment variables
4. Set up systemd services for production
5. Configure reverse proxy (nginx/apache)
```

**Key Features**:
- **System service configuration**: systemd integration
- **Reverse proxy setup**: nginx/Apache configuration examples  
- **SSL/TLS guidance**: Certificate management instructions
- **Performance tuning**: Production optimization recommendations

## Project Maintenance

### Contribution Guidelines
```markdown
# CONTRIBUTING.md - Development standards

## Code Review Process
1. Issue-first development (no PR without corresponding issue)
2. Core team review for integrations and permissions
3. Quality-focused merging decisions
4. Community feedback integration

## Development Standards
- ESLint compliance required
- Prettier formatting enforced
- Test coverage for new features
- Documentation updates for API changes
```

### Announcement System
```json
// extras/support/announcements/
{
  "id": "mobile-app-2025",
  "title": "Mobile App Released", 
  "description": "AnythingLLM mobile app now available",
  "imageUrl": "/announcements/mobile.png",
  "ctaText": "Download Now",
  "ctaUrl": "https://anythingllm.com/mobile"
}
```

**Features**:
- **Version-targeted announcements**: Show announcements to specific versions
- **Rich media support**: Images and call-to-action buttons
- **Centralized management**: JSON-based announcement configuration

## Build and Development Configuration

### Concurrent Development
```json
// package.json - Development orchestration
{
  "devDependencies": {
    "concurrently": "^9.1.2"
  },
  "scripts": {
    "dev:all": "npx concurrently \"yarn dev:server\" \"yarn dev:frontend\" \"yarn dev:collector\""
  }
}
```

**Benefits**:
- **Parallel service development**: All services running simultaneously
- **Unified logging**: Consolidated output from all services
- **Process management**: Automatic restart on file changes

### Environment Management
```bash
# Automated environment setup
"setup:envs": "cp -n ./frontend/.env.example ./frontend/.env && 
               cp -n ./server/.env.example ./server/.env.development && 
               cp -n ./collector/.env.example ./collector/.env"
```

**Features**:
- **Template-based configuration**: Example files for all services
- **Non-destructive copying**: Preserves existing configurations
- **Service-specific environments**: Tailored configurations per service

## Testing and Quality Assurance

### Test Infrastructure
```json
{
  "scripts": {
    "test": "jest"
  },
  "devDependencies": {
    "jest": "^29.7.0"
  }
}
```

**Current State**: Basic Jest setup with room for expansion

### Code Formatting Standards
```javascript
// Prettier configuration via ESLint
rules: {
  "prettier/prettier": "warn"  // Non-blocking formatting warnings
}
```

**Philosophy**: 
- **Developer-friendly**: Warnings rather than errors
- **Automated fixing**: ESLint auto-fix capabilities
- **Consistent style**: Enforced across all file types

## Notable Technical Decisions

### 1. **Monorepo with Service Separation**
**Decision**: Single repository with multiple service directories
**Rationale**:
- Coordinated development across services
- Shared tooling and configuration
- Simplified dependency management
- Unified release process

### 2. **Warning-Based Linting**
**Decision**: ESLint rules set to "warn" instead of "error"
**Rationale**:
- Non-blocking development workflow
- Visible feedback without build failures
- Gradual code quality improvement
- Developer productivity focus

### 3. **Hermes Parser Selection**
**Decision**: Use Facebook's Hermes parser over default
**Rationale**:
- Better JSX parsing capabilities
- Modern JavaScript feature support
- Improved performance for large codebases
- React ecosystem alignment

### 4. **Flow Type Integration**
**Decision**: Include Flow type checking plugin
**Rationale**:
- Gradual type adoption capability
- Facebook ecosystem consistency
- Optional type safety without TypeScript migration

### 5. **Concurrent Development Servers**
**Decision**: Run all services simultaneously in development
**Rationale**:
- Full-stack development efficiency
- Service interaction testing
- Realistic development environment
- Faster feedback loops

This development tooling setup enables efficient, high-quality development while maintaining code consistency and supporting both individual service development and full-stack integration testing.