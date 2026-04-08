---
title: OpenEnv | AI Support Envoy
emoji: 🎧
colorFrom: indigo
colorTo: gray
sdk: docker
pinned: false
---

# 🏢 AI Support Envoy: Enterprise Customer Support Environment

An OpenEnv-compliant environment designed to train agents for high-stakes, multi-step customer support triage and resolution. This environment bridges the gap between raw LLM chat and production-ready support agents.

![Landing Page](/Landing.png) 
> *The professional dashboard included in the Space provides real-time health and API status.*

## 🌟 Real-World Utility
Customer support is a critical bottleneck for growing enterprises. This environment provides a verifiable training ground for:
- **Intelligent Triage**: Automatically categorizing technical vs. billing issues with high precision.
- **SLA Enforcement**: Dynamic prioritization based on customer sentiment and urgency.
- **Complexity Management**: Handling escalations to specialized teams (DevOps, Billing, Compliance) when standard resolution fails.

## 📊 Benchmark results (Qwen 2.5 72B)
Our baseline agent achieved verified success across multiple difficulty levels using the Hugging Face Free Router:
- **Easy (Triage)**: 100% Accuracy (Score: 1.00)
- **Medium (Priority)**: Accurate prioritization following SLA guidelines.
- **Hard (Resolution)**: Robust handling of multi-step resolutions and complex escalations.

## 🛠️ Environment Specification

### Observation Space
The agent receives a rich state context including:
- `current_ticket`: Full ticket details (description, category, priority, sentiment).
- `tickets_remaining`: Current queue depth.
- `current_sla_status`: ok | warning | breached.
- `recent_actions`: History of the current episode (prevents loops).

### Action Space
Agents interact via a structured JSON bridge:
- `action_type`: `categorize` | `prioritize` | `resolve` | `escalate`
- `value`: The decision payload (e.g., category name or resolution steps).
- `reasoning`: Chain-of-thought justification for the action.

## 🏆 Hackathon Compliance
- ✅ **Hugging Face Router Only**: Uses the official `https://router.huggingface.co/v1` for 100% free inference.
- ✅ **OpenAI Client Usage**: Strictly uses the `openai` Python library for all LLM interactions.
- ✅ **Strict Stdout Format**: Implements the mandatory `[START]`, `[STEP]`, and `[END]` logging.
- ✅ **Validated**: Passed `openenv validate .` verification.

## 🚀 Quick Start
```bash
# Verify the environment locally
./venv/bin/openenv validate .

# Run the inference baseline
./venv/bin/python3 inference.py
```

---
*Created for the OpenEnv Hackathon | Submission by punith2001*
