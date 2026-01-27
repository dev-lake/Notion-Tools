# Quick Fix for Cloud Deployment Error

## Error Message
```
Build failed; check build logs for details
The user-provided container failed to start and listen on the port defined
provided by the PORT=8080 environment variable within the allocated timeout.
```

## Solution

The issue has been fixed! Here's what was wrong and how to deploy now:

### What Was Wrong
1. ❌ Container was listening on port 5000 instead of 8080
2. ❌ Health check timeout was too short (5s)
3. ❌ Too many workers (4) for cloud platforms
4. ❌ CMD wasn't using exec form for proper signal handling

### What's Fixed
1. ✅ Container now listens on PORT environment variable (defaults to 8080)
2. ✅ Health check timeout increased to 40s
3. ✅ Reduced to 2 workers + 4 threads (better for cloud)
4. ✅ Proper exec form for signal handling

## Deploy Now

### Option 1: Use Dockerfile.cloud (Recommended for Cloud)

This is optimized specifically for cloud platforms:

```bash
# For Google Cloud Run
gcloud run deploy notion-to-word-converter \
  --source . \
  --dockerfile Dockerfile.cloud \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars FLASK_ENV=production,PORT=8080

# For other platforms, build with:
docker build -f Dockerfile.cloud -t notion-converter .
```

### Option 2: Use Updated Dockerfile

The main Dockerfile has also been fixed:

```bash
docker build -t notion-converter .
docker run -p 8080:8080 -e PORT=8080 notion-converter
```

## Key Configuration

Make sure these environment variables are set:

```bash
PORT=8080                    # Required!
FLASK_ENV=production         # Required!
SECRET_KEY=your-secret-key   # Required!
MAX_CONTENT_LENGTH=104857600 # Optional (100MB default)
```

## Test Locally First

Before deploying to cloud, test locally:

```bash
# Build the cloud-optimized image
docker build -f Dockerfile.cloud -t notion-converter-test .

# Run with PORT=8080
docker run -p 8080:8080 -e PORT=8080 -e FLASK_ENV=production notion-converter-test

# Test in browser
open http://localhost:8080
```

## Platform-Specific Instructions

### Google Cloud Run
```bash
gcloud run deploy notion-to-word-converter \
  --source . \
  --dockerfile Dockerfile.cloud \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300
```

### Railway
1. Push to GitHub
2. Connect repository to Railway
3. Set environment variables:
   - `PORT=8080`
   - `FLASK_ENV=production`
   - `SECRET_KEY=<generate-random>`
4. Railway will auto-deploy

### Render
1. Connect GitHub repository
2. Select "Docker" as environment
3. Set Dockerfile path to `Dockerfile.cloud`
4. Add environment variables
5. Deploy

### Heroku
```bash
heroku container:push web --app your-app-name
heroku container:release web --app your-app-name
```

## Verify Deployment

After deployment, check:

1. **Container logs** - Should show:
   ```
   [INFO] Listening at: http://0.0.0.0:8080
   [INFO] Using worker: sync
   [INFO] Booting worker with pid: X
   ```

2. **Health check** - Should return 200 OK:
   ```bash
   curl https://your-app-url.com/
   ```

3. **Upload test** - Try uploading a small Notion export

## Still Having Issues?

### Check Logs
```bash
# Google Cloud Run
gcloud run services logs read notion-to-word-converter --limit 50

# Railway
railway logs

# Render
# View logs in dashboard
```

### Common Issues

**Issue: "Container failed to start"**
- Solution: Check that PORT=8080 is set
- Verify Dockerfile.cloud is being used

**Issue: "Health check failed"**
- Solution: Increase timeout to 300s
- Check memory allocation (needs 2Gi minimum)

**Issue: "Out of memory"**
- Solution: Increase memory to 2Gi or 4Gi
- Reduce worker count if needed

**Issue: "Request timeout"**
- Solution: Increase timeout to 300s (5 minutes)
- Large files need more processing time

## Need More Help?

See the complete guides:
- [CLOUD_DEPLOY.md](CLOUD_DEPLOY.md) - Full cloud deployment guide
- [DOCKER.md](DOCKER.md) - Docker deployment guide
- [README.md](README.md) - General documentation

## Quick Reference

| Platform | Memory | CPU | Timeout | Workers |
|----------|--------|-----|---------|---------|
| Cloud Run | 2Gi | 2 | 300s | 2 |
| App Runner | 2GB | 1 vCPU | 120s | 2 |
| Railway | 2GB | - | - | 2 |
| Render | 2GB | - | - | 2 |
| Heroku | 1GB+ | - | 30s | 2 |

The deployment should work now! 🚀
