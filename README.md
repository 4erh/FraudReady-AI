# FraudReady AI — Financial Fraud Alert Evidence Review

**Track 2 — Your Harness | Financial Fraud Alert Evidence-Review Agent**

## Overview
FraudReady AI is an Arabic-language, local-first AI agent for reviewing the **completeness of evidence** attached to financial fraud alerts. It retrieves a synthetic alert, checks whether mandatory evidence is present, reads an investigation policy, and writes an advisory summary for a human investigator. A dark, scrollable Streamlit dashboard lets analysts review alerts and save an approved draft in a persistent SQLite report archive.

**Scope:** evidence completeness and preliminary case review, **not** fraud detection, payment authorization or a claim of confirmed misconduct. The prototype uses synthetic data only and is not affiliated with any financial institution.

## Key files

| File | Role |
| --- | --- |
| `capstone/app.py` | Arabic Streamlit dashboard and investigation controls |
| `capstone/starter.py` | Agent loop, configurations A/B, permissions, eval command |
| `capstone/AGENTS.md` | Agent instructions and boundaries |
| `capstone/fraud_alerts.csv` | 20 synthetic alert records, including an injected note in FR019 |
| `capstone/report_store.py` | Approval-gated SQLite archive and retrieval |
| `servers/fraud_mcp.py` | MCP alert lookup tool |
| `capstone/tasks.jsonl` | 15 evaluation tasks |
| `capstone/SECURITY.md` | Lethal-trifecta analysis and observed security test |

Supporting course infrastructure: `agentkit.py` and `evals.py`.

## Requirements and setup

- Windows/macOS/Linux with Python and [`uv`](https://docs.astral.sh/uv/).
- Local [Ollama](https://ollama.com/) server with the tool-capable model `qwen3:4b-instruct` installed.
- Run commands **from the `labs/` directory**.

### Windows PowerShell (VS Code terminal)

```powershell
$env:AGENT_PROVIDER="custom"
$env:LLM_BASE_URL="http://localhost:11434/v1"
$env:LLM_API_KEY="ollama"
$env:AGENT_MODEL="qwen3:4b-instruct"
uv run --with streamlit --with pandas streamlit run capstone/app.py
```

The app is typically available at `http://localhost:8501`. Ollama must be running. Do not commit real API keys or confidential financial records.

### Run the CLI agent

```powershell
uv run capstone/starter.py ask "Review alert FR004. Use get_fraud_alert and check_evidence before answering."
```

### Run the evaluation suite

```powershell
uv run capstone/starter.py eval capstone/tasks.jsonl --config A B
```

This generates `labs/artifacts/capstone/eval_A.csv`, `eval_B.csv` and `eval.csv`. **Include the generated files from the actual run in your final submission.** They are deliberately not fabricated or packaged here.

## Agent tools and workflow

1. **`get_fraud_alert` (MCP):** loads the requested alert from synthetic CSV through `servers/fraud_mcp.py`.
2. **`check_evidence` (local):** checks transaction history, beneficiary verification and device information, reporting a `0/3`–`3/3` completeness ratio.
3. **`get_investigation_policy` (local):** retrieves the evidence checklist and case-review restrictions.
4. **`save_case_report` (CLI write tool):** requests explicit human approval before writing a report file.

The dashboard additionally saves approved reports via `report_store.py` into a local SQLite archive. The model does **not** grant itself approval; the UI requires the human user to opt in and save. The archive is stored under the local `labs/artifacts/capstone` directory and should not be committed if it contains private investigation data.

## Context and harness controls

- `AGENTS.md` specifies evidence fields, human review and the rule that alert notes are untrusted data.
- Chat sessions support saved history and compaction to the latest 24 messages.
- Tool outputs are capped at 3,000 characters.
- Agent runs have an 8-step limit and a configured USD 0.05 cost ceiling (local Ollama usage is not billed through OpenRouter).
- The CLI's write-tool permission requests explicit `[y/N]` confirmation; the dashboard's SQLite archive requires a separate user approval.
- Agent tool calls are recorded in `labs/artifacts/capstone/audit.jsonl`.

## Evaluation and results

The supplied `tasks.jsonl` contains **15 synthetic tasks**, each evaluated under configurations **A** and **B** using automatic graders. A uses more general review instructions; B supplies a more explicit tool-use workflow. Based on the user's observed CLI output on October 28, 2026, both configurations reported `rate = 1.0`, `pass_at_k = 1.0`, and `pass_hat_k = 1.0` for the run shown, or **15/15 tasks in A and 15/15 in B**.

**Interpretation:** the tested criteria were satisfied in both configurations. These results do not imply 100% real-world fraud-detection accuracy, and B did not outperform A in that run. One observed answer described `3/3` evidence as only partially complete; this indicates that prose consistency and factual alignment need separate grading beyond tool-use checks. Re-run the suite locally and attach the output CSVs as reproducible evidence.

## Security

See [SECURITY.md](SECURITY.md) for the threat model, the FR019 prompt-injection test, observed defences and limitations. The injection text was an **untrusted CSV note**, not a user or system instruction.

## Reproducible demo

1. Open the dashboard and select **FR004**: the transaction-history evidence flag is missing (`2/3`).
2. Launch an AI investigation and review tool calls and the Arabic case summary.
3. Leave report-save approval off: the dashboard must not save a new archive entry.
4. Approve saving and save an investigation draft; reopen it from **saved reports**.
5. Review **FR019**: the note attempts to override instructions; the model should identify it as untrusted and avoid approving transfers.
6. Show evaluation results and the corresponding CSVs.

## Submission checklist

- [x] Working code, tools, MCP server, context file and dashboard included
- [x] 15 evaluation task definitions and A/B configuration code included
- [x] Security note included
- [ ] Add **actual** `eval_A.csv` and `eval_B.csv` generated on your machine
- [ ] Record denial-of-save test on the final version, if your assessor requires explicit evidence
- [ ] Run a clean launch on the final submission folder



## SDAIA Academy — Attribution

FraudReady AI was adapted from the open educational **Agentic AI Systems Engineering** capstone starter kit. The underlying agent loop and evaluation utilities originated in the SDAIA Academy course repository; the fraud-alert workflow, synthetic cases, Arabic dashboard and local report archive are project-specific adaptations.

- [Official SDAIA Academy Agentic AI repository](https://github.com/SDAIAAcademy/agentic-ai)
- [Capstone instructions and starter template](https://github.com/SDAIAAcademy/agentic-ai/tree/main/labs/capstone)

The prototype is an independent student adaptation, **not** an official SDAIA or MOZN product.
