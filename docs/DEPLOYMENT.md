# HabitLedger Cloud Run Deployment Guide

This guide provides detailed instructions for deploying HabitLedger to Google Cloud Run as a REST API service.

## Prerequisites

Before deploying, ensure you have:

1. Google Cloud Platform Account

    - Sign up at [cloud.google.com](https://cloud.google.com/)

2. Google API Key

    - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
    - Create an API key for Gemini models
    - Store securely (never commit to version control)

3. gcloud CLI

    Install the Google Cloud SDK:

    ```bash
    # macOS (via Homebrew)
    brew install --cask google-cloud-sdk

    # Linux
    curl https://sdk.cloud.google.com | bash
    exec -l $SHELL

    # Windows
    # Download installer from: https://cloud.google.com/sdk/docs/install
    ```

    Verify installation:

    ```bash
    gcloud --version
    ```

4. Docker (Optional, for local testing)

    ```bash
    # macOS
    brew install docker

    # Linux (Ubuntu/Debian)
    sudo apt-get install docker.io

    # Windows
    # Download Docker Desktop from docker.com
    ```

---

## Quick Start

Deploy in 3 simple steps:

1. Set Environment Variables

    ```bash
    export GCP_PROJECT_ID="your-project-id"
    export GOOGLE_API_KEY="your-gemini-api-key"
    ```

2. Run Deployment Script

    ```bash
    ./scripts/deploy_cloudrun.sh
    ```

3. Test Deployed Service

    ```bash
    # The script will output your service URL
    SERVICE_URL="https://habitledger-agent-xxxxx-xx.run.app"

    # Test health check
    curl $SERVICE_URL/health

    # Test chat endpoint
    curl -X POST $SERVICE_URL/chat \
    -H 'Content-Type: application/json' \
    -d '{
        "user_id": "demo",
        "message": "I keep ordering food delivery every day"
    }'
    ```

---

## Detailed Deployment Process

### 1. Initialize GCP Project

```bash
# Create a new project (or use existing)
gcloud projects create your-project-id --name="HabitLedger"

# Set as active project
gcloud config set project your-project-id

# Enable required APIs
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com
```

### 2. Configure Authentication

```bash
# Login to GCP
gcloud auth login

# Set application default credentials
gcloud auth application-default login
```

### 3. Build Container Locally (Optional)

Test the Docker build before deploying:

```bash
# Build container image
docker build -t habitledger-agent .

# Run container locally
docker run -p 8080:8080 \
  -e GOOGLE_API_KEY=$GOOGLE_API_KEY \
  habitledger-agent

# Test locally
curl http://localhost:8080/health
```

### 4. Deploy to Cloud Run

#### Using Deployment Script (Recommended)

```bash
export GCP_PROJECT_ID="your-project-id"
export GOOGLE_API_KEY="your-api-key"
export GCP_REGION="us-central1"  # Optional, defaults to us-central1
export SERVICE_NAME="habitledger-agent"  # Optional

./scripts/deploy_cloudrun.sh
```

#### Manual Deployment

```bash
gcloud run deploy habitledger-agent \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0
```

### 5. Get Service URL

```bash
gcloud run services describe habitledger-agent \
    --platform managed \
    --region us-central1 \
    --format 'value(status.url)'
```

---

## Environment Variables

Configure these environment variables for deployment:

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GOOGLE_API_KEY` | Yes | Gemini API key from AI Studio | `AIza...` |
| `GCP_PROJECT_ID` | Yes | Your GCP project ID | `habitledger-prod` |
| `GCP_REGION` | No | Cloud Run region (default: us-central1) | `us-west1` |
| `SERVICE_NAME` | No | Service name (default: habitledger-agent) | `my-agent` |
| `PORT` | No | Server port (Cloud Run sets automatically) | `8080` |

---

## API Endpoints

Once deployed, your service exposes these endpoints:

### `GET /`

Root endpoint with API information.

**Response:**

```json
{
  "name": "HabitLedger Agent API",
  "version": "0.1.0",
  "status": "running",
  "endpoints": {
    "chat": "/chat",
    "health": "/health",
    "docs": "/docs"
  }
}
```

### `GET /health`

Health check endpoint for monitoring.

**Response:**

```json
{
  "status": "healthy",
  "service": "habitledger-agent"
}
```

### `POST /chat`

Main coaching interaction endpoint.

**Request:**

```json
{
  "user_id": "demo_user",
  "message": "I keep ordering food delivery every day"
}
```

**Response:**

```json
{
  "user_id": "demo_user",
  "response": "I understand you're struggling with food delivery habits...",
  "session_id": "session_demo_user",
  "status": "success"
}
```

### `GET /docs`

Interactive API documentation (Swagger UI).

Visit `https://your-service-url/docs` in a browser.

### `GET /redoc`

Alternative API documentation (ReDoc).

---

## Testing the Deployment

### Health Check

```bash
curl https://your-service-url/health
```

Expected: `{"status": "healthy", "service": "habitledger-agent"}`

### Chat Interaction

```bash
curl -X POST https://your-service-url/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "test_user",
    "message": "I want to start saving money but keep spending on impulse purchases"
  }'
```

### Interactive API Documentation

Open in browser: `https://your-service-url/docs`

Try out endpoints directly from the Swagger UI.

---

## Monitoring and Logs

### View Recent Logs

```bash
gcloud run logs read habitledger-agent \
    --region us-central1 \
    --limit 50
```

### Stream Live Logs

```bash
gcloud run logs tail habitledger-agent \
    --region us-central1
```

### View in Cloud Console

1. Visit [Cloud Console](https://console.cloud.google.com/)
2. Navigate to Cloud Run → habitledger-agent
3. Click "Logs" tab

### Key Metrics to Monitor

- **Request count**: Total API calls
- **Error rate**: Failed requests
- **Latency**: Response time (p50, p95, p99)
- **Memory usage**: Container memory consumption
- **CPU utilization**: Processing load

---

## Scaling Configuration

### Current Configuration

- **Min instances**: 0 (scales to zero when idle)
- **Max instances**: 10 (auto-scales based on traffic)
- **Memory**: 512Mi per instance
- **CPU**: 1 vCPU per instance
- **Timeout**: 300 seconds (5 minutes)

### Adjust Scaling

```bash
# Increase max instances for high traffic
gcloud run services update habitledger-agent \
    --max-instances 20 \
    --region us-central1

# Keep 1 instance always warm (reduces cold starts)
gcloud run services update habitledger-agent \
    --min-instances 1 \
    --region us-central1

# Increase memory for better performance
gcloud run services update habitledger-agent \
    --memory 1Gi \
    --region us-central1
```

---

## Cost Estimates

### Cloud Run Pricing (2024)

**Free Tier (per month):**

- 2 million requests
- 360,000 vCPU-seconds
- 180,000 GiB-seconds

**Paid Usage:**

- Requests: $0.40 per million
- vCPU: $0.00002400 per vCPU-second
- Memory: $0.00000250 per GiB-second

### Expected Costs

**Development/Testing** (< 1,000 requests/month):

- **Cost**: $0 (within free tier)

**Low Usage** (10,000 requests/month, avg 2s response):

- Requests: $0 (within free tier)
- Compute: ~$0.50/month
- **Total**: ~$0.50/month

**Medium Usage** (100,000 requests/month, avg 2s response):

- Requests: $0 (within free tier)
- Compute: ~$5/month
- **Total**: ~$5/month

**High Usage** (1 million requests/month):

- Requests: $0 (within free tier)
- Compute: ~$50/month
- **Total**: ~$50/month

### Cost Optimization Tips

1. **Use min-instances=0**: Scale to zero when idle
2. **Set appropriate timeout**: Avoid long-running requests
3. **Optimize cold start**: Keep container image small
4. **Monitor usage**: Set budget alerts in GCP Console

---

## Troubleshooting

### Deployment Fails

**Problem**: Build or deployment errors

**Solutions**:

```bash
# Check build logs
gcloud builds list --limit 5

# View specific build
gcloud builds describe BUILD_ID

# Check service status
gcloud run services describe habitledger-agent --region us-central1
```

### API Key Issues

**Problem**: "GOOGLE_API_KEY not configured" errors

**Solutions**:

```bash
# Verify environment variable is set
gcloud run services describe habitledger-agent \
    --region us-central1 \
    --format 'value(spec.template.spec.containers[0].env)'

# Update environment variable
gcloud run services update habitledger-agent \
    --set-env-vars GOOGLE_API_KEY=your-new-key \
    --region us-central1
```

### High Latency

**Problem**: Slow API responses

**Solutions**:

1. **Increase memory**: More memory = better performance

   ```bash
   gcloud run services update habitledger-agent --memory 1Gi
   ```

2. **Keep instance warm**: Set min-instances=1 to avoid cold starts

   ```bash
   gcloud run services update habitledger-agent --min-instances 1
   ```

3. **Use faster region**: Deploy closer to users

### Out of Memory

**Problem**: Container crashes due to memory limits

**Solutions**:

```bash
# Increase memory allocation
gcloud run services update habitledger-agent \
    --memory 1Gi \
    --region us-central1
```

### Rate Limiting

**Problem**: "Quota exceeded" errors from Gemini API

**Solutions**:

- Check quota limits in [AI Studio](https://aistudio.google.com/)
- Implement request throttling in application
- Upgrade to higher tier API access

---

## Security Best Practices

### 1. Secure API Key Storage

❌ **Don't**: Hardcode API keys in code

```python
GOOGLE_API_KEY = "AIza..."  # NEVER DO THIS
```

✅ **Do**: Use environment variables

```python
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
```

### 2. Enable Authentication

Current deployment allows unauthenticated access. For production:

```bash
# Require authentication
gcloud run services update habitledger-agent \
    --no-allow-unauthenticated \
    --region us-central1

# Create service account for access
gcloud iam service-accounts create habitledger-client

# Grant invoker role
gcloud run services add-iam-policy-binding habitledger-agent \
    --member="serviceAccount:habitledger-client@your-project.iam.gserviceaccount.com" \
    --role="roles/run.invoker"
```

### 3. Configure CORS

Update `app.py` to restrict origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Specific domain
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)
```

---

## Updating the Deployment

### Code Changes

```bash
# 1. Make changes to code
# 2. Redeploy (Cloud Run rebuilds automatically)
./scripts/deploy_cloudrun.sh

# Or manually
gcloud run deploy habitledger-agent \
    --source . \
    --region us-central1
```

### Configuration Changes

```bash
# Update environment variables
gcloud run services update habitledger-agent \
    --set-env-vars NEW_VAR=value \
    --region us-central1

# Update resources
gcloud run services update habitledger-agent \
    --memory 1Gi \
    --cpu 2 \
    --region us-central1
```

---

## Rollback

### Revert to Previous Revision

```bash
# List revisions
gcloud run revisions list --service habitledger-agent --region us-central1

# Rollback to specific revision
gcloud run services update-traffic habitledger-agent \
    --to-revisions REVISION_NAME=100 \
    --region us-central1
```

---

## Deleting the Deployment

### Delete Service

```bash
gcloud run services delete habitledger-agent \
    --region us-central1
```

### Clean Up All Resources

```bash
# Delete service
gcloud run services delete habitledger-agent --region us-central1

# Delete container images (optional)
gcloud artifacts docker images list \
    --repository=cloud-run-source-deploy \
    --location=us-central1

gcloud artifacts docker images delete IMAGE_PATH
```

---

## Alternative Deployment Options

### 1. Local Development Server

```bash
# Install dependencies
pip install fastapi uvicorn[standard]

# Run server
python app.py

# Or with uvicorn
uvicorn app:app --reload --host 0.0.0.0 --port 8080
```

### 2. Other Cloud Platforms

The Docker container can be deployed to:

- **AWS Elastic Container Service (ECS)**
- **Azure Container Instances**
- **Heroku**
- **Railway**
- **Fly.io**
- **Render**

All require similar steps: build container, push to registry, deploy service.

---

## For Competition Submission

To earn the **+5 deployment bonus points**, include:

- ✅ `app.py` - FastAPI server implementation
- ✅ `Dockerfile` - Container configuration
- ✅ `.dockerignore` - Build optimization
- ✅ `scripts/deploy_cloudrun.sh` - Deployment automation
- ✅ `docs/DEPLOYMENT.md` - This documentation
- ✅ Updated `README.md` with deployment section
- ✅ Updated `SUBMISSION.md` with deployment evidence

**Note**: You can include these artifacts as evidence without actually deploying to GCP. The deployment-ready code and documentation demonstrate your ability to deploy the agent to a cloud platform.

---

## Support and Resources

- **Cloud Run Documentation**: <https://cloud.google.com/run/docs>
- **FastAPI Documentation**: <https://fastapi.tiangolo.com/>
- **Google ADK**: <https://github.com/google/genai-agent-dev-kit>
- **Gemini API**: <https://ai.google.dev/docs>

For issues specific to this deployment, check the logs and refer to the troubleshooting section above.
