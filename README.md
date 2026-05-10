---
title: Security Code Reviewer
emoji: 🔒
colorFrom: red
colorTo: pink
sdk: docker
app_port: 8000
---

# Security Code Reviewer

AI-powered security code review for Python pull requests.

**Detects:**
- CWE-89: SQL Injection
- CWE-78: Command Injection  
- CWE-22: Path Traversal

**Architecture:**
- LangGraph 4-node DAG
- Bandit static analysis + GPT-4o semantic review
- FastAPI service

**Usage:**
Upload a ZIP file of your Python codebase and provide the PR diff to get security findings.

**API Endpoint:** `POST /review`