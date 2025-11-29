# API Quota Management

## Overview

HabitLedger uses Google's Gemini API for LLM-based behavior analysis. To ensure reliable operation and prevent quota exhaustion, this guide explains how quotas work and how to manage them effectively.

## Understanding API Quotas

### Free Tier Limits

Google's Gemini API free tier has the following limits (as of 2025):

| Model | Requests/Minute | Tokens/Minute |
|-------|-----------------|---------------|
| **gemini-1.5-flash** (recommended) | 15 | 1M input + 30k output |
| gemini-2.0-flash-exp | 10 | 500k input + 10k output |

**Why gemini-1.5-flash is recommended:**

- ✅ Higher quota limits (15 vs 10 requests/min)
- ✅ Stable production model (not experimental)
- ✅ More tokens available per minute
- ✅ Better reliability

### Quota Exhaustion Symptoms

When quotas are exceeded, you'll see:

```text
ClientError: 429 RESOURCE_EXHAUSTED
You exceeded your current quota, please check your plan and billing details.
```

**What happens in HabitLedger:**

1. LLM analysis fails with quota error
2. System automatically falls back to keyword-based detection
3. Warning logged to `habitledger.log`
4. User still receives a valid response (resilient design)

## Built-in Protections

### 1. Rate Limiting

HabitLedger implements automatic rate limiting between LLM calls:

```python
# Default: 1 second between calls
LLM_MIN_CALL_INTERVAL=1.0
```

**Configure in `.env`:**

```bash
# Increase delay for stricter rate limiting (recommended for free tier)
LLM_MIN_CALL_INTERVAL=2.0

# Decrease for paid tier with higher quotas
LLM_MIN_CALL_INTERVAL=0.5
```

### 2. Keyword Fallback

When LLM fails (quota, network, etc.), the system uses keyword-based detection:

- **Coverage:** All 8 behavioral principles supported
- **Speed:** Instant, no API calls
- **Accuracy:** ~70-80% (vs ~90% for LLM)

This ensures HabitLedger **always works**, even without API access.

### 3. Smart Error Handling

The system distinguishes between:

- **Quota errors** → Warning log, graceful fallback
- **Other errors** → Error log with full traceback

## Best Practices

### For Development

```bash
# Use recommended model with better quotas
GOOGLE_ADK_MODEL=gemini-1.5-flash

# Add delays between calls during testing
LLM_MIN_CALL_INTERVAL=2.0

# Monitor quota usage in logs
grep "quota" habitledger.log
```

### For Production

1. **Upgrade to Paid Tier**
   - Visit: <https://ai.google.dev/pricing>
   - Significantly higher quotas
   - More predictable performance

2. **Implement Caching**
   - Cache LLM responses for similar inputs
   - Reduce redundant API calls
   - Example: Store principle detections for common phrases

3. **Batch Processing**
   - Process user inputs in batches with delays
   - Use async/await for concurrent operations
   - Implement request queuing

4. **Monitor Usage**
   - Track API calls per user/session
   - Set up alerts for approaching quota limits
   - Use Google Cloud Monitoring

## Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | (required) | Your Gemini API key |
| `GOOGLE_ADK_MODEL` | `gemini-1.5-flash` | Model to use for LLM analysis |
| `LLM_MIN_CALL_INTERVAL` | `1.0` | Minimum seconds between LLM calls |

### Model Selection

**Choose your model based on needs:**

```bash
# Production: Best balance of quota and performance
GOOGLE_ADK_MODEL=gemini-1.5-flash

# Testing: Experimental features, stricter quotas
GOOGLE_ADK_MODEL=gemini-2.0-flash-exp

# High volume: Paid tier with gemini-1.5-pro
GOOGLE_ADK_MODEL=gemini-1.5-pro
```

## Troubleshooting

### Issue: "Quota exceeded" errors in logs

**Solution:**

1. Check current usage: <https://ai.dev/usage?tab=rate-limit>
2. Increase `LLM_MIN_CALL_INTERVAL` to 2-3 seconds
3. Switch to `gemini-1.5-flash` if using experimental model
4. Consider upgrading to paid tier

### Issue: Too many keyword fallbacks

**Symptoms:**

```bash
# Check detection source distribution
grep "source" habitledger.log | grep -c "keyword"  # High count
grep "source" habitledger.log | grep -c "adk"      # Low count
```

**Solutions:**

1. Verify API key is set correctly
2. Check for quota exhaustion in logs
3. Increase rate limiting delay
4. Wait for quota reset (usually per-minute)

### Issue: Slow response times

**Cause:** Rate limiting introducing delays

**Solutions:**

```bash
# Reduce delay (only if you have higher quotas)
LLM_MIN_CALL_INTERVAL=0.5

# Or accept keyword fallback for some requests
# (faster, no API call, still functional)
```

## Monitoring Quota Usage

### Check Detection Success Rate

```python
# In your code or notebook
from src.behaviour_engine import analyse_behaviour

results = []
for prompt in test_prompts:
    result = analyse_behaviour(prompt, memory, db)
    results.append(result.get("source"))

llm_count = sum(1 for s in results if s == "adk")
keyword_count = sum(1 for s in results if s == "keyword")

print(f"LLM: {llm_count}, Keyword: {keyword_count}")
```

### Check Logs for Quota Issues

```bash
# View recent quota warnings
tail -100 habitledger.log | grep -i "quota"

# Count quota errors today
grep "$(date +%Y-%m-%d)" habitledger.log | grep -c "RESOURCE_EXHAUSTED"

# See which scenarios are hitting quota limits
grep "quota_exceeded" habitledger.log | grep -o "user_input_preview.*" | head -10
```

## Advanced: Caching Implementation

To reduce API calls, implement result caching:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_llm_analysis(user_input_hash: str, memory_hash: str):
    """Cache LLM results for identical inputs."""
    # Your LLM call here
    pass

def analyse_with_cache(user_input, memory, db):
    input_hash = hashlib.md5(user_input.encode()).hexdigest()
    memory_hash = hashlib.md5(str(memory.goals).encode()).hexdigest()
    
    return cached_llm_analysis(input_hash, memory_hash)
```

## Resources

- **Gemini API Quotas:** <https://ai.google.dev/gemini-api/docs/rate-limits>
- **Monitor Usage:** <https://ai.dev/usage?tab=rate-limit>
- **Pricing Plans:** <https://ai.google.dev/pricing>
- **API Documentation:** <https://ai.google.dev/docs>

---

**Key Takeaway:** HabitLedger is designed to be resilient. Even with quota limits, the keyword fallback ensures users always get helpful responses. For production use, consider upgrading to a paid tier for optimal performance.
