#!/bin/bash

echo "Testing CIA Streaming API with curl"
echo "===================================="

# Test 1: Price conscious
echo -e "\n[TEST 1] Price conscious homeowner:"
curl -X POST http://localhost:8008/api/cia/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "I need bathroom work but Im on a tight budget, only $5000"}],
    "conversation_id": "test-price-conscious",
    "user_id": "test-user-001",
    "max_tokens": 500,
    "model_preference": "gpt-5"
  }' \
  --max-time 10 \
  --silent \
  --write-out "\nHTTP Status: %{http_code}\n" | head -20

# Test 2: Urgent repair
echo -e "\n[TEST 2] Urgent repair:"
curl -X POST http://localhost:8008/api/cia/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "HELP! My roof is leaking and its raining!"}],
    "conversation_id": "test-urgent",
    "user_id": "test-user-002",
    "max_tokens": 500,
    "model_preference": "gpt-5"
  }' \
  --max-time 10 \
  --silent \
  --write-out "\nHTTP Status: %{http_code}\n" | head -20

# Test 3: Curious about InstaBids
echo -e "\n[TEST 3] Curious browser:"
curl -X POST http://localhost:8008/api/cia/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "What exactly is InstaBids and how is it different from Angies List?"}],
    "conversation_id": "test-curious",
    "user_id": "test-user-003",
    "max_tokens": 500,
    "model_preference": "gpt-5"
  }' \
  --max-time 10 \
  --silent \
  --write-out "\nHTTP Status: %{http_code}\n" | head -20

echo -e "\nTests complete"