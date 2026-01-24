# Deployment Guide

This guide covers deploying Antigravity to production environments.

## 📋 Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development)
- Node.js 20+ (for frontend builds)
- Access to Google Cloud Platform (for Vertex AI) or Gemini API key
- Domain name and SSL certificate (for production)

## 🔐 Environment Configuration

### Required Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# API Keys
GEMINI_API_KEY=your_api_key_here

# Environment
ENV=production

# CORS Configuration
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
CORS_ALLOW_ALL=false

# Authentication
AGENT_API_KEY=your_secure_api_key_here
AUTH_DISABLED=false

# Model Configuration
DEFAULT_MODEL=models/gemini-2.0-flash
DEFAULT_IMAGE_MODEL=models/gemini-2.0-flash

# Rate Limiting
RATE_LIMIT=100/minute
RATE_LIMIT_DISABLED=false

# Telemetry
PHOENIX_COLLECTOR_ENDPOINT=http://phoenix:6006/v1/traces
OTEL_SERVICE_NAME=antigravity-production
```

### Security Best Practices

1. **Never commit `.env` files** - They are in `.gitignore`
2. **Use secrets management** - In production, use Docker secrets, Kubernetes secrets, or AWS Secrets Manager
3. **Rotate API keys regularly** - Set up a key rotation schedule
4. **Use strong API keys** - Generate cryptographically secure random keys for `AGENT_API_KEY`

## 🐳 Docker Deployment

### Production Docker Compose

For production, create a `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # Use production-specific configurations
  # Remove volume mounts for .env files
  # Add resource limits
  # Configure health checks
```

### Building and Starting

```bash
# Build all services
docker-compose build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Check health
docker-compose ps
```

### Health Checks

All services expose a `/health` endpoint. Monitor these endpoints:

```bash
# Check orchestrator
curl http://localhost:8000/health

# Check dashboard
curl http://localhost:8010/health
```

## 🌐 Reverse Proxy Setup

### Nginx Configuration

Example Nginx configuration for production:

```nginx
upstream dashboard {
    server localhost:8010;
}

upstream orchestrator {
    server localhost:8000;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Dashboard
    location / {
        proxy_pass http://dashboard;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API endpoints
    location /api {
        proxy_pass http://dashboard;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoring & Observability

### Phoenix Tracing

Phoenix runs on port 6006. Access it at `http://yourdomain.com:6006` (behind authentication in production).

### Log Aggregation

Configure log aggregation for production:

1. **Docker Logging Driver**: Configure Docker to send logs to your log aggregation service
2. **Application Logs**: All services emit JSON logs compatible with Cloud Logging
3. **Error Tracking**: Integrate with error tracking services (Sentry, etc.)

### Metrics

Monitor the following metrics:

- Container health status
- API response times
- Rate limit hits
- Error rates
- Resource usage (CPU, memory)

## 🔄 Updates and Rollbacks

### Rolling Updates

```bash
# Pull latest code
git pull origin main

# Rebuild affected services
docker-compose build [service_name]

# Rolling restart
docker-compose up -d --no-deps [service_name]
```

### Rollback Procedure

```bash
# Checkout previous version
git checkout [previous-commit]

# Rebuild and restart
docker-compose build
docker-compose up -d
```

## 🚨 Production Checklist

Before deploying to production:

- [ ] All environment variables configured
- [ ] `.env` file not mounted in Docker (use secrets)
- [ ] CORS configured for production domains only
- [ ] Authentication enabled (`AUTH_DISABLED=false`)
- [ ] Rate limiting enabled
- [ ] Health checks configured
- [ ] Resource limits set on containers
- [ ] SSL/TLS certificates configured
- [ ] Log aggregation configured
- [ ] Monitoring and alerting set up
- [ ] Backup procedures documented
- [ ] Rollback plan tested

## 🔧 Troubleshooting Production Issues

### High Memory Usage

1. Check container resource limits
2. Review logs for memory leaks
3. Scale horizontally if needed

### Slow API Responses

1. Check rate limiting settings
2. Review database/API connection pools
3. Monitor external API latency (Gemini API)

### Authentication Failures

1. Verify `AGENT_API_KEY` is set correctly
2. Check CORS configuration
3. Review authentication logs

### Container Crashes

1. Check health check endpoints
2. Review container logs: `docker-compose logs [service]`
3. Verify resource limits are appropriate
4. Check for dependency issues

## 📈 Scaling

### Horizontal Scaling

To scale agents horizontally:

```bash
# Scale a specific service
docker-compose up -d --scale researcher=3
```

### Load Balancing

Use a load balancer (Nginx, HAProxy) to distribute traffic across multiple instances.

## 🔒 Security Hardening

1. **Network Isolation**: Use Docker networks to isolate services
2. **Secrets Management**: Never store secrets in code or mounted files
3. **Regular Updates**: Keep dependencies and base images updated
4. **Access Control**: Implement proper authentication and authorization
5. **Audit Logging**: Log all authentication attempts and API calls
6. **DDoS Protection**: Use rate limiting and consider CloudFlare or similar

## 📞 Support

For deployment issues:

1. Check logs: `docker-compose logs -f`
2. Review health endpoints
3. Check environment variables
4. Review this troubleshooting guide
