#!/bin/bash
# Test the Node gateway via HTTP webhook
curl -X POST http://localhost:3000/sms/incoming \
  -H "Content-Type: application/json" \
  -d '{"from": "+254711122233", "text": "Registration in Nairobi", "to": "1500"}'
