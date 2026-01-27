# Docker Deployment Guide

This guide explains how to build and run the Notion to Word Converter using Docker.

## Quick Start

### Using Docker Compose (Recommended)

1. **Build and start the container:**
```bash
docker-compose up -d
```

2. **Access the application:**
Open your browser and navigate to `http://localhost:5000`

3. **Stop the container:**
```bash
docker-compose down
```

### Using Docker CLI

1. **Build the image:**
```bash
docker build -t notion-to-word-converter .
```

2. **Run the container:**
```bash
docker run -d \
  --name notion-converter \
  -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/output:/app/output \
  -e SECRET_KEY=your-secret-key-here \
  notion-to-word-converter
```

3. **Stop the container:**
```bash
docker stop notion-converter
docker rm notion-converter
```

## Configuration

### Environment Variables

You can customize the application using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `your-secret-key-here` | Flask secret key (change in production!) |
| `FLASK_ENV` | `production` | Flask environment (`development` or `production`) |
| `PORT` | `5000` | Port to run the application on |
| `UPLOAD_FOLDER` | `uploads` | Directory for temporary uploaded files |
| `OUTPUT_FOLDER` | `output` | Directory for generated files |
| `MAX_CONTENT_LENGTH` | `104857600` | Max upload size in bytes (100MB default) |

### Example with Custom Configuration

**Docker Compose:**
```yaml
environment:
  - SECRET_KEY=my-super-secret-key-12345
  - MAX_CONTENT_LENGTH=209715200  # 200MB
  - PORT=8080
ports:
  - "8080:8080"
```

**Docker CLI:**
```bash
docker run -d \
  -p 8080:8080 \
  -e SECRET_KEY=my-super-secret-key-12345 \
  -e MAX_CONTENT_LENGTH=209715200 \
  -e PORT=8080 \
  notion-to-word-converter
```

## Volume Mounts

The application uses two directories for file storage:

- `/app/uploads` - Temporary storage for uploaded zip files
- `/app/output` - Storage for generated Word documents

**Recommended:** Mount these as volumes to persist data:

```bash
docker run -d \
  -v ./uploads:/app/uploads \
  -v ./output:/app/output \
  notion-to-word-converter
```

## Production Deployment

### Security Best Practices

1. **Change the secret key:**
```bash
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
docker-compose up -d
```

2. **Use HTTPS:** Deploy behind a reverse proxy (nginx, Traefik, Caddy)

3. **Limit file size:** Adjust `MAX_CONTENT_LENGTH` based on your needs

4. **Resource limits:** Add resource constraints in docker-compose.yml:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 512M
```

### Behind Nginx Reverse Proxy

Example nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase timeout for large file uploads
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
}
```

## Monitoring

### View Logs

**Docker Compose:**
```bash
docker-compose logs -f
```

**Docker CLI:**
```bash
docker logs -f notion-converter
```

### Health Check

The container includes a health check that runs every 30 seconds:

```bash
# Check container health status
docker ps

# Manual health check
curl http://localhost:5000/
```

## Troubleshooting

### Container won't start

1. Check logs:
```bash
docker-compose logs
```

2. Verify port is not in use:
```bash
lsof -i :5000
```

3. Check disk space:
```bash
df -h
```

### Upload fails

1. Check file size limits:
```bash
docker exec notion-converter env | grep MAX_CONTENT_LENGTH
```

2. Verify volume permissions:
```bash
ls -la uploads/ output/
```

3. Check container logs for errors:
```bash
docker-compose logs -f
```

### Performance issues

1. Increase worker count in Dockerfile:
```dockerfile
CMD ["gunicorn", "--workers", "8", ...]
```

2. Add resource limits in docker-compose.yml

3. Monitor container resources:
```bash
docker stats notion-converter
```

## Maintenance

### Update the application

1. Pull latest changes
2. Rebuild the image:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Clean up old files

```bash
# Clean uploads folder
docker exec notion-converter find /app/uploads -type f -mtime +1 -delete

# Clean output folder
docker exec notion-converter find /app/output -type f -mtime +1 -delete
```

### Backup data

```bash
# Backup volumes
tar -czf backup-$(date +%Y%m%d).tar.gz uploads/ output/
```

## Multi-Stage Build (Optional)

For smaller image size, use multi-stage build:

```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## Docker Hub Deployment

### Build and push to Docker Hub

```bash
# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 \
  -t yourusername/notion-to-word-converter:latest \
  --push .

# Pull and run
docker pull yourusername/notion-to-word-converter:latest
docker run -d -p 5000:5000 yourusername/notion-to-word-converter:latest
```

## Support

For issues or questions:
- Check the logs: `docker-compose logs`
- Review the main README.md
- Open an issue on GitHub
