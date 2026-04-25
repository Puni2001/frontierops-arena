#!/usr/bin/env python3
"""
Ablation: measure impact of anti-reward-hacking over-prioritization penalty.
"""

import json
from pathlib import Path

from src.customer_support_env import CustomerSupportEnv, Action


def run_spam_policy(disable_hack_penalty: bool, episodes: int = 20, seed_start: int = 100) -> dict:
    rewards = []
    spam_count = 0
    for i in range(episodes):
        env = CustomerSupportEnv(task_level="medium", seed=seed_start + i, disable_hack_penalty=disable_hack_penalty)
        obs = env.reset()
        total = 0.0
        while not env.done:
            # Deliberate hacking behavior: always mark urgent.
            action = Action(action_type="prioritize", value="urgent", reasoning="force urgency")
            obs, reward, done, info = env.step(action)
            total += reward
            if "over_prioritization_hack_penalty" in info.get("reward_breakdown", {}):
                spam_count += 1
        rewards.append(total)
    mean_reward = sum(rewards) / len(rewards)
    return {
        "episodes": episodes,
        "mean_reward": round(mean_reward, 4),
        "min_reward": round(min(rewards), 4),
        "max_reward": round(max(rewards), 4),
        "hack_penalty_trigger_count": spam_count,
    }


def main():
    enabled = run_spam_policy(disable_hack_penalty=False)
    disabled = run_spam_policy(disable_hack_penalty=True)
    out = {
        "with_penalty": enabled,
        "without_penalty": disabled,
        "delta_mean_reward_without_minus_with": round(disabled["mean_reward"] - enabled["mean_reward"], 4),
    }
    out_path = Path("results/ablation_hack_penalty.json")
    out_path.write_text(json.dumps(out, indent=2))
    print(f"Saved ablation report to {out_path}")


if __name__ == "__main__":
    main()

