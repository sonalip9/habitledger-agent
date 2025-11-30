#!/bin/bash
# Local testing script for HabitLedger FastAPI server
# Run this to verify the deployment works before pushing to Cloud Run

set -e

echo "═══════════════════════════════════════════════════════"
echo "   HabitLedger Local Deployment Test"
echo "═══════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if server is running
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Port 8080 is already in use. Stop the existing server first.${NC}"
    exit 1
fi

echo "Starting FastAPI server..."
echo ""

# Start server in background
python app.py &
SERVER_PID=$!

# Give server time to start
sleep 3

# Check if server is running
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo -e "${RED}✗ Server failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Server started (PID: $SERVER_PID)${NC}"
echo ""

# Test endpoints
echo "Testing endpoints..."
echo ""

# Test 1: Root endpoint
echo "1. Testing GET /"
RESPONSE=$(curl -s http://localhost:8080/)
if echo "$RESPONSE" | grep -q "HabitLedger"; then
    echo -e "${GREEN}✓ Root endpoint works${NC}"
else
    echo -e "${RED}✗ Root endpoint failed${NC}"
    kill $SERVER_PID
    exit 1
fi

# Test 2: Health check
echo "2. Testing GET /health"
RESPONSE=$(curl -s http://localhost:8080/health)
if echo "$RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health check works${NC}"
else
    echo -e "${RED}✗ Health check failed${NC}"
    kill $SERVER_PID
    exit 1
fi

# Test 3: Chat endpoint
echo "3. Testing POST /chat"
RESPONSE=$(curl -s -X POST http://localhost:8080/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "test_user",
    "message": "I keep ordering food delivery every day"
  }')
if echo "$RESPONSE" | grep -q "response"; then
    echo -e "${GREEN}✓ Chat endpoint works${NC}"
else
    echo -e "${RED}✗ Chat endpoint failed${NC}"
    echo "Response: $RESPONSE"
    kill $SERVER_PID
    exit 1
fi

# Test 4: OpenAPI docs
echo "4. Testing GET /docs"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/docs)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ OpenAPI docs available${NC}"
else
    echo -e "${RED}✗ OpenAPI docs failed (HTTP $HTTP_CODE)${NC}"
    kill $SERVER_PID
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo -e "${GREEN}✓ All tests passed!${NC}"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Server is running at http://localhost:8080"
echo ""
echo "Try these commands:"
echo "  curl http://localhost:8080/health"
echo "  curl http://localhost:8080/docs"
echo "  curl -X POST http://localhost:8080/chat \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"user_id\": \"demo\", \"message\": \"I want to save money\"}'"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Wait for user interrupt
wait $SERVER_PID
