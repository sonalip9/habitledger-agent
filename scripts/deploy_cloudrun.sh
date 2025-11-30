#!/bin/bash
set -e

# HabitLedger Cloud Run Deployment Script
# This script deploys the HabitLedger agent to Google Cloud Run

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-habitledger-agent}"
GOOGLE_API_KEY="${GOOGLE_API_KEY}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "═══════════════════════════════════════════════════════"
echo "   HabitLedger Cloud Run Deployment"
echo "═══════════════════════════════════════════════════════"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}✗ gcloud CLI not found. Please install: https://cloud.google.com/sdk/docs/install${NC}"
    exit 1
fi
echo -e "${GREEN}✓ gcloud CLI found${NC}"

if [ -z "$GOOGLE_API_KEY" ]; then
    echo -e "${RED}✗ GOOGLE_API_KEY environment variable not set${NC}"
    echo "  Set it with: export GOOGLE_API_KEY=your_api_key"
    exit 1
fi
echo -e "${GREEN}✓ GOOGLE_API_KEY configured${NC}"

# Set project
echo ""
echo "Setting GCP project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo ""
echo "Enabling required GCP APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com

# Build and deploy
echo ""
echo "Building and deploying to Cloud Run..."
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --format 'value(status.url)')

echo ""
echo "═══════════════════════════════════════════════════════"
echo -e "${GREEN}✓ Deployment successful!${NC}"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Service URL: $SERVICE_URL"
echo ""
echo "Test the deployment:"
echo "  curl $SERVICE_URL/health"
echo ""
echo "  curl -X POST $SERVICE_URL/chat \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"user_id\": \"demo\", \"message\": \"I keep ordering food delivery\"}'"
echo ""
echo "View logs:"
echo "  gcloud run logs read $SERVICE_NAME --region $REGION --limit 50"
echo ""
echo "═══════════════════════════════════════════════════════"
