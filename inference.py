#!/usr/bin/env python3
"""
FrontierOps Arena — Inference Script
====================================
STDOUT FORMAT (mandatory):
  [START] task=<task_name> env=<benchmark> model=<model_name>
  [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
  [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
"""

import os
import json
import time
import sys
from typing import List, Optional, Dict
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

from src.customer_support_env import CustomerSupportEnv, Action, KNOWLEDGE_BASE
from tasks.grader import TaskGrader

# ── Config ──────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME",   "Qwen/Qwen2.5-0.5B-Instruct")
HF_TOKEN     = os.getenv("HF_TOKEN")
BENCHMARK    = "customer-support-env"
TEMPERATURE  = 0.2

# ── Logging ─────────────────────────────────────────────────

def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]):
    err = error or "null"
    act = str(action).replace("\n", " ")[:80]
    print(f"[STEP] step={step} action={act} reward={reward:.4f} done={str(done).lower()} error={err}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    rewards_str = ",".join(f"{r:.4f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.4f} rewards={rewards_str}", flush=True)

# ── Agent ────────────────────────────────────────────────────
from src.agent import SupportAgent

# ── Task Runner ──────────────────────────────────────────────

def run_task(task_level: str, agent: SupportAgent, seed: Optional[int] = None) -> Dict:
    log_start(task_level, BENCHMARK, MODEL_NAME)

    env = CustomerSupportEnv(task_level=task_level, seed=seed)
    obs = env.reset()
    rewards: List[float] = []
    actions: List[Dict] = []
    step = 0
    max_steps = env.task_config["max_steps"]

    while not env.done and step < max_steps:
        step += 1
        action = agent.get_action(obs, task_level)

        # Build action record for grader
        rec: Dict = {"reasoning": action.reasoning or ""}
        if action.action_type == "categorize":
            rec["categorization"] = action.value
        elif action.action_type == "prioritize":
            rec["priority"] = action.value
            rec["categorization"] = obs.current_ticket.category.value if obs.current_ticket else ""
        elif action.action_type == "resolve":
            rec["resolution"] = action.value
            rec["escalated"] = False
            rec["resolved_within_sla"] = obs.current_sla_status != "breached"
        elif action.action_type == "escalate":
            rec["escalated"] = True
            rec["resolution"] = action.value
            rec["resolved_within_sla"] = obs.current_sla_status != "breached"

        actions.append(rec)

        try:
            obs, reward, done, info = env.step(action)
            rewards.append(reward)
            log_step(step, f"{action.action_type}({action.value[:40]})", reward, done, None)
        except Exception as e:
            log_step(step, f"{action.action_type}(error)", 0.0, False, str(e)[:60])
            break

    # Grade
    score = 0.0
    graders = {
        "easy": lambda: TaskGrader.grade_easy(actions, env.tickets),
        "medium": lambda: TaskGrader.grade_medium(actions, env.tickets),
        "hard": lambda: TaskGrader.grade_hard(actions, env.tickets),
        "chaos": lambda: TaskGrader.grade_chaos(actions, env.tickets),
    }
    if task_level in graders:
        score = graders[task_level]()

    success = score >= 0.6
    log_end(success, step, score, rewards)

    return {"task": task_level, "score": score, "steps": step, "rewards": rewards, "success": success}

# ── Main ─────────────────────────────────────────────────────

def main():
    if not HF_TOKEN:
        print("Error: HF_TOKEN environment variable not set.", file=sys.stderr)
        sys.exit(1)

    agent = SupportAgent(MODEL_NAME, HF_TOKEN, API_BASE_URL)
    results = []

    tasks = ["easy", "medium", "hard"]
    # Optionally run chaos mode
    if os.getenv("RUN_CHAOS", "false").lower() == "true":
        tasks.append("chaos")

    for task in tasks:
        result = run_task(task, agent, seed=42)
        results.append(result)
        time.sleep(2)  # brief pause between tasks

    # Summary
    print("\n=== SUMMARY ===", flush=True)
    for r in results:
        status = "PASS" if r["success"] else "FAIL"
        avg_r = sum(r["rewards"]) / max(1, len(r["rewards"]))
        print(f"[{status}] {r['task']:25s} score={r['score']:.4f}  avg_reward={avg_r:.4f}  steps={r['steps']}", flush=True)

if __name__ == "__main__":
    main()
