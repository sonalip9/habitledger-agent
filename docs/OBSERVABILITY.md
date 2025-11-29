# HabitLedger Observability & Logging

> **Complete Guide**: Observability implementation, structured logging, performance metrics, and production monitoring for HabitLedger Agent

## Table of Contents

- [Overview](#overview)
- [Implementation Summary](#implementation-summary)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Log Event Types](#log-event-types)
- [Key Metrics](#key-metrics)
- [Usage Examples](#usage-examples)
- [Log Analysis](#log-analysis-queries)
- [Integration](#integration-with-observability-tools)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Evaluation](#evaluation--testing)

## Overview

HabitLedger implements comprehensive observability through structured logging, enabling:

- **Decision transparency**: Track why the agent chose specific principles and interventions
- **Performance monitoring**: Measure response times, LLM latency, and tool execution
- **Error tracking**: Detailed error context with stack traces for debugging
- **Session analytics**: Track user progress, engagement patterns, and intervention effectiveness

## Implementation Summary

### What Was Implemented

Comprehensive observability was added to HabitLedger for decision transparency, performance monitoring, and production debugging:

- **Structured logging** with human-readable and key=value formats
- **Event-based tracking** covering 10+ distinct event types
- **Performance metrics** including duration_ms and latency tracking
- **Decision context** capturing principle_id, confidence, and detection source

### Files Modified

1. **`src/config.py`** - Logging configuration with structured format support
2. **`src/llm_client.py`** - LLM performance and decision tracking  
3. **`src/memory.py`** - State change logging for memory operations
4. **`src/habitledger_adk/runner.py`** - Session analytics and interaction tracking
5. **`src/coach.py`, `src/habitledger_adk/agent.py`** - Tool call and response generation tracking

### Quick Start

```bash
# Standard logging
python -m src.coach

# Structured logging (for log aggregation tools)
STRUCTURED_LOGGING=true python -m src.coach

# Debug mode (verbose output)
LOG_LEVEL=DEBUG python -m src.habitledger_adk.runner
```

### Benefits

✅ **Decision Transparency** - Understand why agent chose specific principles  
✅ **Performance Monitoring** - Track LLM latency and response times  
✅ **Error Debugging** - Detailed context for troubleshooting  
✅ **Evaluation** - Log-based metrics for agent quality assessment  
✅ **Production Ready** - Enterprise-grade logging practices

## Architecture

### Logging Layers

```text
┌─────────────────────────────────────────────────┐
│         Application Layer                        │
│  (coach.py, behaviour_engine.py, agent.py)      │
│  - Decision logging                              │
│  - Principle detection                           │
│  - Intervention selection                        │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│         Integration Layer                        │
│  (llm_client.py, habitledger_adk/)              │
│  - LLM request/response logging                  │
│  - Tool call tracking                            │
│  - Performance metrics                           │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│         Persistence Layer                        │
│  (memory.py, session_db.py)                     │
│  - State change logging                          │
│  - Memory operations                             │
│  - Session persistence                           │
└─────────────────────────────────────────────────┘
```

## Configuration

### Basic Setup

```python
from src.config import setup_logging

# Standard logging (human-readable)
setup_logging(level="INFO")

# Debug mode (verbose)
setup_logging(level="DEBUG")

# Structured logging (for observability tools)
setup_logging(level="INFO", structured=True)
```

### Environment Variables

```bash
# Set log level
export LOG_LEVEL=DEBUG

# Enable structured logging (key=value format)
export STRUCTURED_LOGGING=true

# Logs will include:
# timestamp=2025-11-25 10:30:00 level=INFO module=src.coach 
# function=run_once line=123 message=Behaviour analysis complete
```

## Log Event Types

### 1. LLM Analysis Events

**Event: `llm_analysis_start`**

```python
{
    "event": "llm_analysis_start",
    "user_input_preview": "I keep ordering food delivery...",
    "memory_goals_count": 2,
    "memory_streaks_count": 1
}
```

**Event: `llm_analysis_complete`**

```python
{
    "event": "llm_analysis_complete",
    "principle_id": "friction_increase",
    "reason": "User mentions easy access to delivery apps",
    "intervention_count": 3,
    "triggers_count": 2,
    "total_duration_ms": 1250,
    "source": "adk"
}
```

**Event: `llm_analysis_failed`**

```python
{
    "event": "llm_analysis_failed",
    "reason": "no_function_call",
    "duration_ms": 800
}
```

### 2. Tool Call Events

**Event: `tool_call`** (behaviour_db_tool)

```python
{
    "event": "tool_call",
    "tool_name": "behaviour_db_tool",
    "principle_id": "loss_aversion",
    "source": "adk",
    "user_input": "I broke my SIP streak...",
    "duration_ms": 50
}
```

**Event: `tool_call`** (ADK agent)

```python
{
    "event": "tool_call",
    "tool_name": "behaviour_db_tool",
    "principle_id": "habit_loops",
    "source": "adk",
    "duration_ms": 45
}
```

### 3. Response Generation Events

**Event: `response_generation`**

```python
{
    "event": "response_generation",
    "source": "adk",  # or "template"
    "tool_used": true,
    "response_length": 342,
    "user_input": "I keep ordering food...",
    "duration_ms": 1500
}
```

**Event: `low_confidence_handling`**

```python
{
    "event": "low_confidence_handling",
    "principle_id": "micro_habits",
    "confidence": 0.55
}
```

### 4. Memory & Session Events

**Event: `memory_save`**

```python
{
    "event": "memory_save",
    "user_id": "user123",
    "file_path": "/data/user123.json",
    "goals_count": 3,
    "streaks_count": 2,
    "interventions_count": 5,
    "conversations_count": 12
}
```

**Event: `session_memory_save`**

```python
{
    "event": "session_memory_save",
    "session_id": "session_user123",
    "user_id": "user123",
    "goals_count": 3,
    "active_streaks": 1,
    "total_streaks": 2,
    "struggles_count": 2,
    "conversation_turns": 8
}
```

**Event: `interaction_recorded`**

```python
{
    "event": "interaction_recorded",
    "user_id": "user123",
    "outcome_type": "intervention",
    "streak_name": null,
    "principle_id": "friction_increase",
    "timestamp": "2025-11-25T10:30:00"
}
```

**Event: `session_interaction`**

```python
{
    "event": "session_interaction",
    "session_id": "session_demo_user",
    "user_id": "demo_user",
    "interventions": 3,
    "conversation_turns": 5,
    "response_length": 280,
    "session_events": 10
}
```

## Key Metrics

### Performance Metrics

| Metric | Description | Typical Range |
|--------|-------------|---------------|
| `total_duration_ms` | End-to-end LLM analysis time | 800-2000ms |
| `llm_duration_ms` | LLM API call time | 600-1500ms |
| `tool_duration_ms` | Tool execution time | 10-100ms |
| `response_length` | Character count of response | 150-500 chars |

### Decision Metrics

| Metric | Description |
|--------|-------------|
| `principle_id` | Which behavioral principle was detected |
| `source` | Detection method: "adk" (LLM) or "keyword" (fallback) |
| `confidence` | Confidence score: 0.0-1.0 |
| `intervention_count` | Number of interventions suggested |

### Session Metrics

| Metric | Description |
|--------|-------------|
| `conversation_turns` | Total user-assistant exchanges |
| `active_streaks` | Number of ongoing habit streaks |
| `interventions` | Total interventions provided |
| `session_events` | ADK session events logged |

## Usage Examples

### 1. Track Agent Decisions

```python
import logging

logger = logging.getLogger(__name__)

# The agent automatically logs its decision-making:
# 2025-11-25 10:30:00 [INFO] src.behaviour_engine.analyse_behaviour:89 - 
# LLM analysis successful 
# {principle_id: friction_increase, confidence: 0.85, duration_ms: 1200}
```

### 2. Monitor Performance

```bash
# Filter for performance metrics
grep "duration_ms" habitledger.log | grep "llm_analysis_complete"

# Example output:
# 2025-11-25 10:30:00 [INFO] ... total_duration_ms=1250
# 2025-11-25 10:31:15 [INFO] ... total_duration_ms=980
# 2025-11-25 10:32:30 [INFO] ... total_duration_ms=1150
```

### 3. Analyze Fallback Patterns

```bash
# Count LLM vs keyword detections
grep "source" habitledger.log | sort | uniq -c

# Example output:
# 45 source=adk
#  5 source=keyword
```

### 4. Debug Session Issues

```python
# All session operations are automatically logged:
logger.info("Session state saved", extra={
    "session_id": session.id,
    "user_id": user_id,
    "active_streaks": 2,
    "conversation_turns": 8
})
```

## Log Analysis Queries

### Python Log Analysis

```python
import json
import re
from collections import Counter

def analyze_logs(log_file):
    """Analyze HabitLedger logs for insights."""
    
    # Count principle detections
    principles = Counter()
    sources = Counter()
    durations = []
    
    with open(log_file) as f:
        for line in f:
            if "principle_id" in line:
                match = re.search(r"principle_id[=:](\w+)", line)
                if match:
                    principles[match.group(1)] += 1
            
            if "source" in line:
                match = re.search(r"source[=:](\w+)", line)
                if match:
                    sources[match.group(1)] += 1
            
            if "duration_ms" in line:
                match = re.search(r"duration_ms[=:](\d+)", line)
                if match:
                    durations.append(int(match.group(1)))
    
    print("Top 5 Principles:")
    for principle, count in principles.most_common(5):
        print(f"  {principle}: {count}")
    
    print("\nDetection Sources:")
    for source, count in sources.items():
        print(f"  {source}: {count}")
    
    if durations:
        print(f"\nPerformance:")
        print(f"  Avg duration: {sum(durations)/len(durations):.0f}ms")
        print(f"  Min duration: {min(durations)}ms")
        print(f"  Max duration: {max(durations)}ms")

# Usage
analyze_logs("habitledger.log")
```

### Shell Analysis

```bash
# Count by event type
grep -o 'event=[a-z_]*' habitledger.log | sort | uniq -c

# Average LLM latency
grep "llm_duration_ms" habitledger.log | 
    grep -o 'llm_duration_ms=[0-9]*' | 
    cut -d= -f2 | 
    awk '{sum+=$1; count++} END {print sum/count "ms"}'

# Most common principles
grep -o 'principle_id=[a-z_]*' habitledger.log | 
    sort | uniq -c | sort -rn | head -5

# Session summary
grep "session_interaction" habitledger.log | tail -1
```

## Integration with Observability Tools

### 1. Structured Logging for ELK Stack

```python
# Enable structured logging
setup_logging(level="INFO", structured=True)

# Logs are now in key=value format, easily parsed by Logstash:
# timestamp=2025-11-25 10:30:00 level=INFO event=llm_analysis_complete 
# principle_id=friction_increase duration_ms=1250
```

### 2. JSON Logging for Datadog/Splunk

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "module": record.name,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        if hasattr(record, "event"):
            log_data.update(record.__dict__)
        return json.dumps(log_data)

# Use custom formatter
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.getLogger().addHandler(handler)
```

### 3. Prometheus Metrics Export

```python
from prometheus_client import Counter, Histogram

# Define metrics
principle_detections = Counter(
    'habitledger_principle_detections_total',
    'Total principle detections',
    ['principle_id', 'source']
)

llm_duration = Histogram(
    'habitledger_llm_duration_seconds',
    'LLM analysis duration'
)

# Update in your code
principle_detections.labels(
    principle_id=result["detected_principle_id"],
    source=result["source"]
).inc()

llm_duration.observe(duration_ms / 1000)
```

## Best Practices

### 1. Log Levels

- **DEBUG**: Detailed diagnostic information (LLM prompts, full responses)
- **INFO**: Normal operation events (principle detection, interventions)
- **WARNING**: Unexpected but handled situations (LLM fallback, low confidence)
- **ERROR**: Error conditions that need attention (API failures, invalid state)

### 2. Sensitive Data

```python
# Always truncate user input in logs
user_input_safe = user_input[:100] if len(user_input) > 100 else user_input

logger.info(
    "Processing user input",
    extra={"user_input_preview": user_input_safe}  # Truncated
)
```

### 3. Performance Logging

```python
import time

def log_performance(func):
    """Decorator to log function performance."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration_ms = int((time.time() - start) * 1000)
        
        logger.info(
            f"{func.__name__} completed",
            extra={
                "function": func.__name__,
                "duration_ms": duration_ms
            }
        )
        return result
    return wrapper
```

### 4. Error Context

```python
try:
    result = risky_operation()
except Exception as e:
    logger.error(
        "Operation failed",
        extra={
            "error_type": type(e).__name__,
            "error_message": str(e),
            "context": {"user_id": user_id}
        },
        exc_info=True  # Include stack trace
    )
```

## Troubleshooting

### Problem: No logs appearing

**Solution:**

```python
# Ensure logging is configured
from src.config import setup_logging
setup_logging(level="DEBUG")
```

### Problem: Too verbose logs

**Solution:**

```bash
# Set higher log level
export LOG_LEVEL=WARNING

# Or filter in code
logging.getLogger("src.llm_client").setLevel(logging.WARNING)
```

### Problem: Can't find specific events

**Solution:**

```bash
# Search by event type
grep "event=llm_analysis_complete" habitledger.log

# Search by user_id
grep "user_id=user123" habitledger.log
```

## Evaluation & Testing

### Log-Based Evaluation

The observability system enables automated evaluation:

```python
def evaluate_from_logs(log_file):
    """Evaluate agent performance from logs."""
    
    total_analyses = 0
    llm_successes = 0
    keyword_fallbacks = 0
    avg_confidence = 0
    
    with open(log_file) as f:
        for line in f:
            if "llm_analysis_complete" in line:
                total_analyses += 1
                llm_successes += 1
                
                # Extract confidence
                match = re.search(r"confidence[=:]([0-9.]+)", line)
                if match:
                    avg_confidence += float(match.group(1))
            
            elif "source=keyword" in line:
                keyword_fallbacks += 1
    
    print(f"Total analyses: {total_analyses}")
    print(f"LLM success rate: {llm_successes/total_analyses*100:.1f}%")
    print(f"Keyword fallback rate: {keyword_fallbacks/total_analyses*100:.1f}%")
    print(f"Avg confidence: {avg_confidence/total_analyses:.2f}")
```

## Conclusion

HabitLedger's observability system provides:

- ✅ **Full decision transparency**: Track every principle detection and intervention
- ✅ **Performance insights**: Monitor LLM latency and system responsiveness  
- ✅ **Error diagnostics**: Detailed context for debugging issues
- ✅ **Session analytics**: Understand user engagement and progress patterns
- ✅ **Production readiness**: Structured logs compatible with enterprise tools

For questions or feature requests, see the main [README.md](../README.md).
