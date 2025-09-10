# Docker Setup for AnythingLLM Django Server

This directory contains Docker configuration files for running AnythingLLM in containerized environments.

## Quick Start

### Development Environment

1. **Copy environment file**:
   ```bash
   cp .env.sample .env
   # Edit .env with your configuration
   ```

2. **Build and start services**:
   ```bash
   docker-compose up -d
   ```

3. **Run initial setup**:
   ```bash
   # Run migrations
   docker-compose exec web python manage.py migrate

   # Create superuser
   docker-compose exec web python manage.py createsuperuser

   # Collect static files
   docker-compose exec web python manage.py collectstatic --noinput
   ```

4. **Access the application**:
   - Main app: http://localhost:8000
   - Admin: http://localhost:8000/admin
   - API docs: http://localhost:8000/api/docs
   - pgAdmin: http://localhost:5050 (dev profile only)
   - Flower: http://localhost:5555 (dev profile only)

### Production Environment

1. **Use production compose file**:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

2. **Configure SSL certificates**:
   - Place certificates in `docker/ssl/`
   - Update nginx.conf with your domain
   - Uncomment HTTPS server block

## Services

### Core Services

| Service | Port | Description |
|---------|------|-------------|
| **web** | 8000 | Django application (Daphne/Gunicorn) |
| **db** | 5432 | PostgreSQL database |
| **redis** | 6379 | Cache and message broker |
| **celery** | - | Background task worker |
| **celerybeat** | - | Scheduled task runner |
| **nginx** | 80/443 | Reverse proxy and static files |

### Development Services

Enable with `--profile dev`:

| Service | Port | Description |
|---------|------|-------------|
| **pgadmin** | 5050 | Database management UI |
| **flower** | 5555 | Celery monitoring UI |

## Commands

### Service Management

```bash
# Start all services
docker-compose up -d

# Start with development tools
docker-compose --profile dev up -d

# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION: deletes data)
docker-compose down -v

# View logs
docker-compose logs -f [service_name]

# Restart a service
docker-compose restart [service_name]
```

### Django Management

```bash
# Run Django management commands
docker-compose exec web python manage.py [command]

# Common commands:
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --noinput
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py test
```

### Database Operations

```bash
# Access PostgreSQL shell
docker-compose exec db psql -U anythingllm

# Create database backup
docker-compose exec db pg_dump -U anythingllm anythingllm > backup.sql

# Restore database backup
docker-compose exec -T db psql -U anythingllm anythingllm < backup.sql

# Access pgAdmin (if running)
# Navigate to http://localhost:5050
# Login: admin@anythingllm.com / admin
```

### Celery Operations

```bash
# Monitor Celery workers
docker-compose logs -f celery

# Restart Celery worker
docker-compose restart celery

# Access Flower monitoring (if running)
# Navigate to http://localhost:5555
```

### Debugging

```bash
# Access container shell
docker-compose exec web /bin/bash

# Run Django shell
docker-compose exec web python manage.py shell_plus

# Check service health
docker-compose ps

# View resource usage
docker stats

# Inspect network
docker network inspect django_server_anythingllm_network
```

## Environment Variables

Key variables to configure in `.env`:

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,your-domain.com

# Database (handled by docker-compose)
DATABASE_URL=postgresql://anythingllm:anythingllm@db:5432/anythingllm

# Redis (handled by docker-compose)
REDIS_URL=redis://redis:6379/0

# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=your-api-key

# Vector Database
VECTOR_DB=pinecone
PINECONE_API_KEY=your-api-key
```

## Volumes

Persistent data is stored in Docker volumes:

| Volume | Description | Backup Priority |
|--------|-------------|-----------------|
| `postgres_data` | Database files | Critical |
| `redis_data` | Cache and session data | Low |
| `static_volume` | Static files | Medium |
| `media_volume` | User uploads | Critical |
| `pgadmin_data` | pgAdmin config | Low |

### Backup Volumes

```bash
# Backup a volume
docker run --rm -v django_server_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Restore a volume
docker run --rm -v django_server_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

## Scaling

### Horizontal Scaling

```bash
# Scale Celery workers
docker-compose up -d --scale celery=4

# Scale web workers (requires load balancer configuration)
docker-compose up -d --scale web=3
```

### Resource Limits

Add to docker-compose.yml for production:

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Monitoring

### Health Checks

All services include health checks. Monitor with:

```bash
# Check all services
docker-compose ps

# Detailed health status
docker inspect django_server_web_1 --format='{{json .State.Health}}'
```

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web

# Last 100 lines
docker-compose logs --tail=100 web

# Since timestamp
docker-compose logs --since="2024-01-01T00:00:00" web
```

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Find process using port
   lsof -i :8000
   # Change port in docker-compose.yml or stop conflicting service
   ```

2. **Database connection failed**:
   ```bash
   # Check if database is ready
   docker-compose exec db pg_isready
   # Restart database
   docker-compose restart db
   ```

3. **Static files not loading**:
   ```bash
   # Recollect static files
   docker-compose exec web python manage.py collectstatic --noinput --clear
   # Check nginx logs
   docker-compose logs nginx
   ```

4. **Celery tasks not processing**:
   ```bash
   # Check Celery logs
   docker-compose logs celery
   # Restart Celery
   docker-compose restart celery celerybeat
   ```

5. **Out of disk space**:
   ```bash
   # Clean up unused images and containers
   docker system prune -a
   # Remove unused volumes (CAUTION)
   docker volume prune
   ```

### Reset Everything

```bash
# Stop all services and remove everything
docker-compose down -v
docker system prune -a
# Then start fresh
docker-compose up -d
```

## Security Considerations

1. **Change default passwords** in production
2. **Use SSL certificates** for HTTPS
3. **Restrict database access** to internal network
4. **Set strong SECRET_KEY** in production
5. **Disable DEBUG** in production
6. **Use firewall rules** to restrict ports
7. **Regular security updates** for base images
8. **Implement rate limiting** in nginx
9. **Use secrets management** for sensitive data
10. **Regular backups** of critical volumes

## Performance Tuning

### Django Optimization

```python
# In settings.py for production
CONN_MAX_AGE = 600  # Database connection pooling
ATOMIC_REQUESTS = True  # Database transactions

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50}
        }
    }
}
```

### PostgreSQL Tuning

```sql
-- In postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
random_page_cost = 1.1
```

### Redis Configuration

```conf
# In redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment](https://docs.djangoproject.com/en/4.2/howto/deployment/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Redis Docker Image](https://hub.docker.com/_/redis)
- [Nginx Docker Image](https://hub.docker.com/_/nginx)