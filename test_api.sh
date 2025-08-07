#!/bin/bash

# ScrapIt API Testing Script
echo "🧪 ScrapIt API Testing with cURL"
echo "=================================="

BASE_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4
    
    echo -e "\n${YELLOW}Testing: $description${NC}"
    echo "→ $method $endpoint"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$BASE_URL$endpoint")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST -H "Content-Type: application/json" -d "$data" "$BASE_URL$endpoint")
    fi
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS:.*//g')
    
    if [ $http_code -lt 400 ]; then
        echo -e "${GREEN}✅ Success ($http_code)${NC}"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    elif [ $http_code -lt 500 ]; then
        echo -e "${YELLOW}⚠️  Client Error ($http_code)${NC}"
        echo "$body"
    else
        echo -e "${RED}❌ Server Error ($http_code)${NC}"
        echo "$body"
    fi
}

# Check if server is running
echo "🏥 Checking if server is running..."
if ! curl -s "$BASE_URL/health" > /dev/null; then
    echo -e "${RED}❌ Server is not running!${NC}"
    echo "Please start the server first:"
    echo "  python start_server.py"
    exit 1
fi

echo -e "${GREEN}✅ Server is running${NC}"

# Test basic endpoints
test_endpoint "GET" "/" "Root endpoint"
test_endpoint "GET" "/health" "Health check"

# Test authentication
test_endpoint "GET" "/auth/google" "Google OAuth URL"

# Test chatbot (will fail without auth, but shows structure)
test_endpoint "POST" "/chat/chat" "Chatbot (no auth)" '{"message": "Hello"}'

# Test email endpoints (will fail without auth)
test_endpoint "GET" "/gmail/emails" "Get emails (no auth)"
test_endpoint "GET" "/ai/categories" "Get categories (no auth)"

echo -e "\n${YELLOW}📝 Notes:${NC}"
echo "• Most endpoints require authentication"
echo "• Use /docs for interactive testing"
echo "• Set up .env file for full functionality"

echo -e "\n${GREEN}🚀 Next steps:${NC}"
echo "1. Visit http://localhost:8000/docs for interactive API testing"
echo "2. Set up Google OAuth and OpenAI keys in .env"
echo "3. Test the full authentication flow"