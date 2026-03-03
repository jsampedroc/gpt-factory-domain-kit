# IA Software Factory — Domain Kit (Hexagonal Spring Boot)

This repository contains a **Python-based autonomous software factory** that generates a **Java Spring Boot** project following **Hexagonal Architecture**.

## Core principles

- **Factory in Python**
- **Output: Java Spring Boot (Maven, Java 17) with Hexagonal Architecture**
- **Contract-first domain** (domain layer is framework-agnostic)
- **Guided generation** (the model follows explicit layer contracts)

## Quick start

1) Create a `.env` with your API keys:

```bash
OPENAI_API_KEY=...
DEEPSEEK_API_KEY=...
AI_BASE_URL=https://api.deepseek.com/v1
AI_SMART_MODEL=gpt-4o
AI_CHEAP_MODEL=deepseek-chat
```

2) Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3) Configure the project name:

- `config/architecture.yaml` → `project.name`

4) Run the factory:

```bash
python3 main.py "Build a dental clinic system with patients, appointments, and billing"
```

Output will be written under:

- `outputs/<project_slug>/backend/...`

## Hexagonal contracts

The factory enforces layer rules using:

- `config/layer_contracts.yaml`

If generated code violates the rules (e.g., `jakarta.*` imports in `domain/`), the factory **fails fast**.

## Legacy

Older prototype scripts were moved to `legacy/`.
# gpt-factory-domain-kit
