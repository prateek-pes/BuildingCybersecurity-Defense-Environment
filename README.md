---
title: OpenEnv Cybersecurity
emoji: 🛡️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# OpenEnv Cybersecurity Defense

A fully compliant real-world OpenEnv simulation environment where an AI agent attempts to defend a simulated network environment from varying threats.

## Architecture

* **Environment State (`env/cyber_env.py`)**: Runs an automated 10-step episode logic deciding attack probability (None, DDoS, Malware, Zero-day) based on task difficulty level.
* **API (`api/server.py`)**: Provides the `reset()`, `step()`, and `state()` standard required for OpenEnv.
* **UI**: A premium, state-of-the-art cyberpunk telemetry dashboard that polls the server for attack vector visualization and system health.
* **Baseline Inference (`inference.py`)**: A runnable openAI python baseline answering "block_ip", "scan_system", "deploy_patch", or "ignore". Emits structured logs.

## Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the Server:
```bash
uvicorn api.server:app --port 7860
```
3. Open `http://localhost:7860` in the browser.

## Running the Inference Agent

Ensure the server is running on `http://localhost:7860`.

```bash
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4o-mini"
export HF_TOKEN="<your_openai_key>"
python inference.py
```

## Docker / HF Deployments

You can build the Dockerfile and deploy this directly to Hugging Face Spaces:
```bash
docker build -t openenv-cyberdefense .
docker run -p 7860:7860 openenv-cyberdefense
```
