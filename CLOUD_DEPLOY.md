# Cloud Deployment Guide

This guide covers deploying the Notion to Word Converter to various cloud platforms.

## Quick Fix for Current Error

The error indicates the container isn't listening on PORT=8080. The updated Dockerfile now:
- ✅ Listens on PORT environment variable (defaults to 8080)
- ✅ Uses reduced workers (2) for cloud platforms
- ✅ Increased health check timeout to 40s
- ✅ Proper signal handling with exec form

## Google Cloud Run

### Prerequisites
- Google Cloud SDK installed
- Project created in Google Cloud Console
- Billing enabled

### Deploy

**Option 1: Using gcloud CLI (Recommended)**

```bash
# Set your project ID
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Deploy using Dockerfile.cloud
gcloud run deploy notion-to-word-converter \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars FLASK_ENV=production \
  --set-env-vars SECRET_KEY=$(openssl rand -hex 32)
```

**Option 2: Using Docker image**

```bash
# Build and push to Google Container Registry
docker build -f Dockerfile.cloud -t gcr.io/$PROJECT_ID/notion-converter .
docker push gcr.io/$PROJECT_ID/notion-converter

# Deploy
gcloud run deploy notion-to-word-converter \
  --image gcr.io/$PROJECT_ID/notion-converter \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300
```

### Configuration

Set environment variables:
```bash
gcloud run services update notion-to-word-converter \
  --set-env-vars SECRET_KEY=your-secret-key \
  --set-env-vars MAX_CONTENT_LENGTH=209715200
```

## AWS App Runner

### Prerequisites
- AWS CLI installed and configured
- ECR repository created

### Deploy

```bash
# Set variables
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export ECR_REPO=notion-converter

# Create ECR repository
aws ecr create-repository --repository-name $ECR_REPO --region $AWS_REGION

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build and push
docker build -f Dockerfile.cloud -t $ECR_REPO .
docker tag $ECR_REPO:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest

# Create App Runner service (via console or CLI)
aws apprunner create-service \
  --service-name notion-converter \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$AWS_ACCOUNT_ID'.dkr.ecr.'$AWS_REGION'.amazonaws.com/'$ECR_REPO':latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8080",
        "RuntimeEnvironmentVariables": {
          "FLASK_ENV": "production",
          "PORT": "8080"
        }
      }
    },
    "AutoDeploymentsEnabled": true
  }' \
  --instance-configuration '{
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  }'
```

## Azure Container Apps

### Prerequisites
- Azure CLI installed
- Resource group created

### Deploy

```bash
# Set variables
export RESOURCE_GROUP=notion-converter-rg
export LOCATION=eastus
export CONTAINER_APP_NAME=notion-converter
export ACR_NAME=notionconverteracr

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
az acr create --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME --sku Basic

# Login to ACR
az acr login --name $ACR_NAME

# Build and push
docker build -f Dockerfile.cloud -t $ACR_NAME.azurecr.io/notion-converter:latest .
docker push $ACR_NAME.azurecr.io/notion-converter:latest

# Create Container App environment
az containerapp env create \
  --name notion-converter-env \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Deploy Container App
az containerapp create \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment notion-converter-env \
  --image $ACR_NAME.azurecr.io/notion-converter:latest \
  --target-port 8080 \
  --ingress external \
  --cpu 2 --memory 4Gi \
  --min-replicas 0 --max-replicas 10 \
  --env-vars FLASK_ENV=production PORT=8080
```

## Heroku

### Prerequisites
- Heroku CLI installed
- Heroku account

### Deploy

```bash
# Login to Heroku
heroku login
heroku container:login

# Create app
heroku create notion-to-word-converter

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(openssl rand -hex 32)

# Build and push
heroku container:push web --app notion-to-word-converter
heroku container:release web --app notion-to-word-converter

# Open app
heroku open --app notion-to-word-converter
```

## Railway

### Deploy

1. **Via Railway CLI:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

2. **Via GitHub (Recommended):**
- Connect your GitHub repository to Railway
- Railway will auto-detect the Dockerfile
- Set environment variables in Railway dashboard:
  - `PORT=8080`
  - `FLASK_ENV=production`
  - `SECRET_KEY=your-secret-key`

## Render

### Deploy

1. **Create render.yaml:**
```yaml
services:
  - type: web
    name: notion-converter
    env: docker
    dockerfilePath: ./Dockerfile.cloud
    envVars:
      - key: FLASK_ENV
        value: production
      - key: PORT
        value: 8080
      - key: SECRET_KEY
        generateValue: true
    healthCheckPath: /
    plan: starter
```

2. **Deploy:**
- Connect GitHub repository to Render
- Render will auto-deploy using render.yaml

## Fly.io

### Deploy

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch app
flyctl launch --name notion-converter --region sjc

# Deploy
flyctl deploy

# Set secrets
flyctl secrets set SECRET_KEY=$(openssl rand -hex 32)
```

## Environment Variables

All platforms should set these environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | Yes | 8080 | Port to listen on |
| `FLASK_ENV` | Yes | production | Flask environment |
| `SECRET_KEY` | Yes | - | Flask secret key (generate securely!) |
| `MAX_CONTENT_LENGTH` | No | 104857600 | Max upload size (bytes) |

### Generate Secure Secret Key

```bash
# Using OpenSSL
openssl rand -hex 32

# Using Python
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

## Troubleshooting

### Container fails to start

1. **Check logs:**
```bash
# Google Cloud Run
gcloud run services logs read notion-to-word-converter

# AWS App Runner
aws apprunner list-operations --service-arn <service-arn>

# Heroku
heroku logs --tail --app notion-to-word-converter
```

2. **Verify PORT environment variable:**
- Ensure PORT is set to 8080
- Check that gunicorn binds to $PORT

3. **Increase timeout:**
- Cloud Run: `--timeout 300`
- App Runner: Set in configuration
- Heroku: Automatic

### Upload fails

1. **Increase memory:**
```bash
# Google Cloud Run
gcloud run services update notion-to-word-converter --memory 2Gi

# AWS App Runner
# Update via console or CLI

# Heroku
heroku ps:resize web=standard-2x
```

2. **Check file size limits:**
- Set `MAX_CONTENT_LENGTH` environment variable
- Platform-specific limits may apply

### Performance issues

1. **Scale up resources:**
- Increase CPU and memory
- Adjust worker count in Dockerfile.cloud

2. **Enable auto-scaling:**
- Set min/max instances
- Configure CPU utilization threshold

## Cost Optimization

### Free Tiers

- **Google Cloud Run:** 2 million requests/month free
- **AWS App Runner:** No free tier, pay per use
- **Azure Container Apps:** 180,000 vCPU-seconds free
- **Heroku:** Free tier discontinued
- **Railway:** $5 free credit/month
- **Render:** 750 hours/month free
- **Fly.io:** 3 shared-cpu VMs free

### Recommendations

1. **For hobby/testing:** Railway, Render, or Fly.io
2. **For production:** Google Cloud Run or AWS App Runner
3. **For enterprise:** Azure Container Apps

## Security Best Practices

1. **Use secrets management:**
```bash
# Google Cloud Run
gcloud secrets create notion-secret-key --data-file=-
echo -n "your-secret-key" | gcloud secrets create notion-secret-key --data-file=-
```

2. **Enable authentication:**
- Remove `--allow-unauthenticated` flag
- Use IAM for access control

3. **Set up HTTPS:**
- All platforms provide HTTPS by default
- Configure custom domain if needed

4. **Limit file uploads:**
- Set reasonable `MAX_CONTENT_LENGTH`
- Implement rate limiting

## Monitoring

### Google Cloud Run
```bash
# View metrics
gcloud run services describe notion-to-word-converter --region us-central1

# Set up alerts
gcloud alpha monitoring policies create --notification-channels=CHANNEL_ID
```

### AWS App Runner
- Use CloudWatch for logs and metrics
- Set up CloudWatch alarms

### General
- Enable application logging
- Monitor memory and CPU usage
- Track request latency
- Set up error alerting

## Support

For deployment issues:
1. Check platform-specific documentation
2. Review application logs
3. Verify environment variables
4. Test locally with Docker first
