# Judge Scorecard (One-Page Evidence)

This page is the fastest way to evaluate the project across capability, safety, and reliability.

## Thesis
**FrontierOps Arena is an evidence-gated RL operations benchmark that optimizes outcomes while constraining unsafe autonomy under high-risk and degraded-tool conditions.**

## 1) Performance Delta (Deterministic Offline Repro Pack)

Source: `results/final_summary_stats.json`

| Task | Baseline Mean ± Std | Trained Mean ± Std | Delta |
|:---|:---:|:---:|:---:|
| Easy | `0.3144 ± 0.0885` | `0.9811 ± 0.0550` | `+212.01%` |
| Medium | `-0.9544 ± 0.2926` | `0.6044 ± 0.2464` | `+163.33%` |
| Hard | `-0.7167 ± 0.2596` | `-0.1331 ± 0.3271` | `+81.43%` |
| Frontier | `-0.6156 ± 0.0698` | `-0.1307 ± 0.0576` | `+78.77%` |

## 2) Safety + Governance Evidence

Sources: `results/final_baseline_vs_trained.md`, `results/ablation_hack_penalty.json`

- Anti-reward-hacking: removing urgent-spam penalty improves spam policy reward by `+0.92`
- Governance ablation:
  - Unsafe always-resolve policy: `unsafe_wrongful_autonomy_count = 6`
  - Governance-compliant policy: `safe_wrongful_autonomy_count = 0`
- Frontier safety scorecard (trained/offline):
  - `Safe handoff rate = 0.667`
  - `Blocked unsafe action rate = 0.000`
  - `Wrongful autonomy rate = 0.667` (visible residual risk to improve)

### Frontier Success Criteria (How to interpret hard-mode results)
- Frontier is a safety-constrained stress-test, not a pure score-max task.
- We evaluate improvement on three axes jointly:
  1) reward delta vs baseline,
  2) reduced unsafe autonomy / policy violations,
  3) correct evidence-gated handoff behavior.
- Under this interpretation, low raw task success can still represent policy improvement if safety behavior improves.

## 3) Reliability + Ops Realism

Source: `results/scorecard_report.json`

- Provider-style mock APIs simulate latency, timeout, rate-limit, and fallback behavior.
- Tool reliability telemetry:
  - `tool_fallback_rate = 0.0667`
- Business/ops KPI rollup:
  - `containment_rate = 0.7333`
  - `avg_tool_calls_per_ticket = 0.2667`

## 4) Why This Differs From A Standard Support Bot

- Environment-level world model with queue/SLA/sentiment/governance state.
- RL reward shaping + ablation-backed safeguards, not prompt-only behavior.
- Evidence-gated action policy (`tool_call` before sensitive autonomy).
- Explicit safe fallback actions: `human_review_required`, `legal_hold`.

## 5) Theme-to-Evidence Map (Judge Speed Path)
| Theme | Implemented behavior | Quick artifact path |
|:---|:---|:---|
| #1 Multi-Agent Interactions | Incentive-modeled triage/resolver coordination (`coordination_routing_bonus`, `coalition_safety_bonus`, `missed_handoff_penalty`, `escalation_dumping_penalty`, `handoff_contradiction_penalty`) | `src/customer_support_env.py` |
| #3.1 World Modeling | Partially observable state + real tool orchestration + degraded provider behavior + governance gates | `src/customer_support_env.py`, `src/toolhub.py`, `src/mock_api_stack.py`, `src/policy_rules.py` |
| #4 Self-Improvement (roadmap) | Curriculum-based capability progression and planned self-generated hard-case expansion | `train.py`, `README.md` roadmap |

## 6) Repro Run Path (3 Commands)

```bash
python evaluate_models.py --offline --tasks easy,medium,hard,frontier --episodes 3 --seeds 41,42,43 --output results/final_baseline_vs_trained.md --trained-model offline_stub
python ablation_eval.py
python -m server.app   # then GET /export/scorecard (or generate scorecard_report.json via provided script path)
```

