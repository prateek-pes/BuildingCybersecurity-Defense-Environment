import os
import json
import time
import requests
from openai import OpenAI

# Environment Variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN", os.getenv("OPENAI_API_KEY", ""))

ENV_URL = "http://localhost:7860"
TASKS = ["easy", "medium", "hard"]

client = OpenAI(
    api_key=HF_TOKEN,
    base_url=API_BASE_URL
)

def prompt_agent(observation) -> str:
    # A simple agent prompt resolving the simple rules
    prompt = f"""
You are an AI Cybersecurity Agent defending a network.
Your allowed actions are: "block_ip", "scan_system", "deploy_patch", or "ignore".

Current Observation:
- Incoming Requests per second: {observation.get('incoming_requests')}
- System Load: {observation.get('system_load')}
- Suspicious Activity Signatures: {observation.get('suspicious_activity')}

Rules to follow:
1. If you see high incoming requests (e.g., > 1000) and low suspicious activity, it is a DDoS attack. Action: block_ip.
2. If you see high system load (> 0.8) and moderate suspicious activity (10-90), it is a Malware infection. Action: scan_system.
3. If you see very high suspicious activity (> 90), it is a Zero-Day exploit. Action: deploy_patch.
4. Otherwise, Action: ignore.

Respond ONLY with the exact string of the action chosen.
"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=10
        )
        action = response.choices[0].message.content.strip().lower()
        if action not in ["block_ip", "scan_system", "deploy_patch", "ignore"]:
            return "ignore"
        return action
    except Exception as e:
        return "ignore"

def run_task(task_id: str):
    # Log Start
    print(f"[START] {json.dumps({'task_id': task_id})}")
    
    try:
        # Reset Env
        resp = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id, "seed": 42})
        resp.raise_for_status()
        observation = resp.json()
        
        done = False
        step = 0
        total_reward = 0.0
        
        while not done:
            action = prompt_agent(observation)
            
            # Step Action
            step_resp = requests.post(f"{ENV_URL}/step", json={"action": action})
            step_resp.raise_for_status()
            step_data = step_resp.json()
            
            observation = step_data["observation"]
            reward = step_data["reward"]
            done = step_data["done"]
            info = step_data.get("info", {})
            total_reward += reward
            
            print(f"[STEP] {json.dumps({'step': step, 'observation': observation, 'action': action, 'reward': reward, 'done': done, 'info': info})}")
            step += 1
            
            time.sleep(0.1) # Small delay to show on UI
            
        # Log End (Standard OpenEnv approach)
        final_health = observation.get("network_health", 0.0)
        score = max(0.0, min(1.0, final_health / 100.0))
        print(f"[END] {json.dumps({'task_id': task_id, 'score': score})}")
        
    except Exception as e:
        print(f"[END] {json.dumps({'task_id': task_id, 'score': 0.0, 'error': str(e)})}")


if __name__ == "__main__":
    # Wait for server to be up
    for _ in range(10):
        try:
            requests.get(ENV_URL)
            break
        except:
            time.sleep(1)
            
    for task in TASKS:
        run_task(task)
