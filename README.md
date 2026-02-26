<div align="center">
  <img src="frontend/public/animated.gif" alt="ELYX Logo" width="120" />
  <h1>ELYX</h1>
  <p><strong>A Local-First Autonomous AI Employee Framework</strong></p>

  [![Prototype](https://img.shields.io/badge/Status-Prototype-orange?style=for-the-badge)]()
  [![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
  [![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![Next.js](https://img.shields.io/badge/Frontend-Next.js%2015-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
  [![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
  [![Hackathon](https://img.shields.io/badge/Built%20for-Personal%20AI%20Employee%20Hackathon%200-purple?style=for-the-badge)]()
</div>

---

## 🌐 Overview

**ELYX** is a modular AI employee framework designed to autonomously manage structured business workflows on a local machine while optionally integrating with cloud services.

The system combines:

- **Local data control** and long-term memory (Obsidian vault)
- **A swappable multi-model reasoning core** (Claude, Gemini, Qwen, Codex)
- **Role-based task execution** with human-in-the-loop approvals
- **Cryptographically verifiable action logs** for audit trails

ELYX is built to explore how autonomous AI agents can safely operate within real-world business environments without compromising data sovereignty.

Developed as part of the **Personal AI Employee Hackathon 0**.

---

## 🚀 Core Capabilities

### 🧠 Modular Reasoning Engine

Supports multiple AI providers (Claude, Gemini, Qwen, Codex) that can be switched via environment configuration. This enables experimentation with different reasoning profiles depending on task complexity.

### 👤 Role-Based Task Assignment

Agents operate under defined roles (e.g., Operations, Finance, Communications), limiting scope and improving predictability of execution.

### 📊 Business Workflow Integration

Integrated with Odoo Cloud for:

- Invoice monitoring
- Financial summaries
- Automated reporting

The system can generate structured weekly briefings based on business data.

### 🔐 Local-First Memory & Security

- Long-term memory stored locally (Markdown-based vault)
- Credentials never leave the host environment
- All executed actions are cryptographically signed for traceability

### ⏱ Continuous Monitoring Architecture

Lightweight watcher processes monitor connected services (email, ERP, etc.) and trigger reasoning cycles when predefined conditions are met.

### 🛡️ Human-in-the-Loop Safety

Sensitive actions (payments, new contacts, file sharing) require explicit user approval before execution.

---

## 🏗 System Architecture

ELYX follows a modular, event-driven architecture:

### 1. Perception Layer (Watchers)
Monitors external services and normalizes incoming data:
- Gmail watcher (OAuth2 authenticated)
- WhatsApp watcher (Playwright-based)
- Filesystem watcher (watchdog)
- Odoo ERP watcher (JSON-RPC)

### 2. Reasoning Layer (Brain Core)
Executes structured multi-step decision pipelines using the selected model provider:
- Supports Claude, Gemini, Qwen, Codex via `brain_factory.py`
- Uses Ralph Wiggum pattern for multi-step task persistence
- Creates `Plan.md` files for complex multi-step tasks

### 3. Execution Layer (Skills)
Performs deterministic actions such as:
- Sending emails
- Updating ERP entries
- Generating reports
- Moving files between workflow states

### 4. Audit Layer
Logs and cryptographically signs every strategic action for traceability:
- SHA3-512 hashing via `quantum_resistant_hash.py`
- Append-only audit trail in `audit_trail.json`
- Daily logs in `/Logs/YYYY-MM-DD_Audit.json`

---

## 🛠 Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Backend** | FastAPI (Python) | High-performance API server |
| **Frontend** | Next.js 15 (TypeScript) | Dashboard UI |
| **Database** | SQLite + Supabase | Hybrid storage |
| **Memory** | Obsidian (Local Markdown) | Long-term memory & GUI |
| **ERP Integration** | Odoo Cloud | Accounting & business logic |
| **Security** | SHA3-512 | Cryptographic action signing |
| **Model Support** | Claude, Gemini, Qwen, Codex | Swappable reasoning engines |

---

## 🧪 Current Status

**✅ GOLD TIER COMPLETE (100%)** – All Gold Tier requirements implemented and tested.
Actively expanding automation capabilities and safety constraints.

### ✅ Implemented (Production-Ready)

**Bronze Tier**
- [x] Obsidian vault structure
- [x] File-based task orchestration
- [x] Basic watcher pattern
- [x] Dashboard.md updates

**Silver Tier**
- [x] Gmail watcher (OAuth2 authenticated)
- [x] WhatsApp watcher (Playwright-based)
- [x] Filesystem watcher (watchdog)
- [x] Calendar service integration (optional)
- [x] Predictive analytics service (basic)

**Gold Tier** ✅ **100% COMPLETE**
- [x] Odoo Cloud integration (JSON-RPC)
- [x] Weekly CEO briefing generation
- [x] Human-in-the-loop approval workflow
- [x] Multi-brain support (Claude, Qwen, Gemini, Codex)
- [x] **Social media auto-posting** (LinkedIn, Facebook, Twitter, Instagram)
- [x] **Error recovery with exponential backoff**
- [x] **Windows Task Scheduler integration**
- [x] Comprehensive audit logging
- [x] Ralph Wiggum autonomous loop

**Platinum Tier (Basic)**
- [x] SHA3-512 action signing
- [x] Blockchain-style immutable audit log (single-node simulation)
- [x] Ralph Wiggum autonomous loop

### 🚧 In Development (Prototype)

- [ ] LinkedIn watcher (authentication pending)
- [ ] Facebook/Twitter/Instagram watchers (API integration needed)
- [ ] Multi-region sync (requires actual cloud infrastructure)
- [ ] Federated learning (design phase)

### 📋 Planned (Not Yet Implemented)

- [ ] True quantum-resistant cryptography (NIST PQC standards)
- [ ] Distributed blockchain (currently single-node append-only log)
- [ ] Global failover (requires multi-region deployment)
- [ ] AR/VR interfaces (conceptual)
- [ ] Bio-neural interfaces (research concept only)

### 🧪 Experimental (Use at Your Own Risk)

- Consciousness emergence engine
- Reality simulation module
- Existential reasoning engine
- Temporal reasoning engine

These modules are research prototypes and not recommended for production use.

---

## 🛰 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Anthropic API Key (or other supported AI provider)
- Odoo Cloud Instance (Invoicing App) - optional

### Installation

1. **Clone & Setup Backend**:
   ```bash
   pip install -r requirements.txt
   python run_complete_system.py
   ```

2. **Setup Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Configure Environment**:
   Initialize your `.env` with your Odoo, API, and Security keys.

---

## 🔀 Brain Selection

ELYX supports multiple AI coding agents as its reasoning core. Switch brains by editing one line in `.env`:

```env
# Options: claude, qwen, gemini, codex
ELYX_ACTIVE_BRAIN=claude
```

| Brain | Best For |
| :--- | :--- |
| `claude` | Strategic reasoning, complex multi-step tasks |
| `qwen` | Fast local coding, lightweight operations |
| `gemini` | High-volume triage, analysis, speed |
| `codex` | Code generation and refactoring |

---

## 🛡 Security & Data Sovereignty

- **Local Vault**: Credentials and memories never leave your machine
- **Action Signing**: All strategic actions are cryptographically signed (SHA3-512)
- **Audit Trail**: Immutable append-only log for compliance and debugging
- **Human-in-the-Loop**: Sensitive actions require explicit approval

---

## 📚 Documentation

- [Architecture Overview](ARCHITECTURE.md)
- [Implementation Status](IMPLEMENTATION_STATUS.md)
- [Company Handbook](obsidian_vault/Company_Handbook.md)
- [Skill Documentation](SKILL.md)

---

<div align="center">
  <p>Built for the Personal AI Employee Hackathon 0</p>
  <sub>Open Source - MIT License</sub>
</div>
