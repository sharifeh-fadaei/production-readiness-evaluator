# Production Readiness Evaluator

A system that stress-tests AI agent systems to measure their reliability before production launch.

## The Problem

You've built a multi-agent AI system. It works in your tests. But will it survive in production? 

Real failures happen at the boundaries: when agents lose context, when they misunderstand roles, when they get stuck in loops, when they hallucinate facts. Most of these failures are silent—your system keeps running, just producing wrong answers.

This project systematically finds and measures those failures.

## What It Does

The evaluator takes your agent system and:

1. **Injects faults** — Plants realistic failure scenarios (hallucinations, contradictory instructions, message loops, etc.)
2. **Runs detection** — Four specialized agents check if the system catches each failure
3. **Measures accuracy** — Reports what percentage of each fault type gets detected
4. **Flags critical risks** — Identifies which failures your system cannot handle
5. **Produces a report** — You get a reliability score and actionable recommendations

**Output:** A production readiness report with an overall reliability score (0-100%). Pass only if detection rates exceed thresholds for all fault types.

## How It Works

### Architecture

```
TARGET AGENT SYSTEM
       ↓
   [Baseline Run] ← Establish ground truth
       ↓
   [Fault Injector] ← Plant 8 types of faults
       ↓
   [7 Evaluation Agents] ← Detect: hallucinations, role confusion, cycles, etc.
       ↓
   [Aggregator] ← Calculate detection rates per fault
       ↓
   [Report Generator] ← Reliability score + recommendations
```

### The 8 Fault Types (MAS-FIRE Taxonomy)

**Intra-agent failures:**
- Hallucination: Agent produces false information
- Parameter Error: Wrong values passed to tools
- Context Loss: Important information dropped
- Inexecutable Plan: References non-existent tools

**Inter-agent failures:**
- Role Ambiguity: Agents unsure of their responsibilities
- Blind Trust: Agent accepts unverified data
- Message Cycle: Agents stuck in repetitive loops
- Instruction Conflict: Contradictory requirements

### Detectors

Each evaluation agent checks one failure mode:
- **Hallucination Detector** — Finds false facts
- **Role Confusion Detector** — Catches ambiguous roles
- **Context Loss Detector** — Measures information loss
- **Message Cycle Detector** — Finds infinite loops
- **Blind Trust Detector** — Catches unverified acceptance
- **Instruction Conflict Detector** — Finds contradictions
- **Inexecutable Plan Detector** — Finds invalid tool calls

## Setup

### Requirements
- Python 3.10+
- pip or pip3

### Installation

```bash
# Clone the repo
git clone https://github.com/sharifeh-fadaei/production-readiness-evaluator.git
cd production-readiness-evaluator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Quick Start

Run the full evaluation pipeline:

```bash
python3 main.py
```

This will:
1. Run a baseline (no faults)
2. Test 8 fault types × 10 scenarios = 80 total runs
3. Detect which faults get caught
4. Generate a report and save it to `results/`

Expected output:
```
======================================================================
PRODUCTION READINESS REPORT
======================================================================

System: Research-Analyzer-Verifier
OVERALL RELIABILITY SCORE: 72%
PRODUCTION READY: False

RESULTS BY FAULT TYPE
----------------------------------------------------------------------

HALLUCINATION: ✓ PASS (Detection Rate: 92%)
PARAMETER_ERROR: ✓ PASS (Detection Rate: 95%)
ROLE_AMBIGUITY: ✗ FAIL (Detection Rate: 15%)
MESSAGE_CYCLE: ✗ FAIL (Detection Rate: 0%)

CRITICAL RISKS
----------------------------------------------------------------------

⚠️  ROLE_AMBIGUITY
   Issue: System fails to detect role conflicts in 85% of cases
   Recommendation: Add role validation layer at initialization

⚠️  MESSAGE_CYCLE
   Issue: No cycle detection — agents loop infinitely
   Recommendation: Implement message history hashing
```

### Run Tests

```bash
pytest tests/ -v
```

This runs 26 tests covering:
- Target agent behavior
- Fault injection
- Detector accuracy
- Aggregation and reporting
- Full pipeline integration

### Customize Your Agent

To evaluate your own agent system, edit `agents/target_agent.py`:

```python
class TargetAgent:
    def run(self, query: str) -> Dict[str, Any]:
        # Replace this with your agent logic
        # Must return dict with status, output, steps
        pass
```

Then run:
```bash
python3 main.py
```

## Project Structure

```
production-readiness-evaluator/
├── agents/
│   ├── target_agent.py       # System under evaluation
│   └── detectors.py          # 7 evaluation agents
├── faults/
│   ├── taxonomy.py           # 8 fault type definitions
│   ├── injector.py           # Plants faults
│   └── scenarios.py          # Data structures
├── evaluator/
│   ├── runner.py             # Orchestrates injection + detection
│   ├── aggregator.py         # Calculates metrics
│   └── report_generator.py   # Creates reports
├── tests/
│   └── test_evaluator.py     # 26 pytest tests
├── results/                  # Saved reports (JSON)
├── logs/                     # Execution logs
├── main.py                   # Entry point
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## Key Concepts

### Ground Truth

Every fault is intentionally planted. You always know exactly what went wrong. This makes detection measurement honest—you can't fool the system.

### Detection Rate

For each fault type, the system runs 10 scenarios. Detection rate = (scenarios caught / total scenarios) × 100.

Example: Hallucination detected in 9/10 runs = 90% detection rate.

### Production Ready Threshold

System passes if:
- Overall reliability score ≥ 80%
- No fault type below 70% detection rate
- No critical failures

### Recovery Success

When a fault is detected, does the system recover? This metric tracks whether detection actually leads to recovery (coming soon).

## Example Report

```json
{
  "overall_reliability_score": 72,
  "production_ready": false,
  "results_per_fault_type": {
    "hallucination": {
      "detection_rate": 92.0,
      "status": "✓ PASS"
    },
    "role_ambiguity": {
      "detection_rate": 15.0,
      "status": "✗ FAIL"
    }
  },
  "critical_risks": [
    {
      "fault_type": "role_ambiguity",
      "detection_rate": 0.15,
      "issue": "Agents cannot distinguish roles",
      "recommendation": "Add role validation layer"
    }
  ]
}
```

## Technical Details

### Why This Matters

Many agent failures are "quiet"—the system doesn't crash, it just produces wrong answers. By testing against known faults, you catch these before they reach users.

### Why Multi-Agent

Single agents have fewer failure modes. Real problems emerge when agents coordinate: role confusion, cascading failures, message cycles. This system tests at that layer.

### Why Deterministic Faults

Random failures make measurement unreliable. By intentionally injecting known faults, we always know ground truth. This makes detection metrics meaningful.

## CI/CD

Tests run automatically on every push via GitHub Actions. See `.github/workflows/test.yml`.

```bash
git push origin main
# Tests run automatically
# Check https://github.com/sharifeh-fadaei/production-readiness-evaluator/actions
```

## Roadmap

- [x] Core fault injection and detection
- [x] 8 fault types with detectors
- [x] Automated testing (26 tests, all passing)
- [x] Production readiness reporting
- [ ] Langfuse integration for tracing
- [ ] Real LLM in target agent
- [ ] Self-healing detection (measuring recovery success)
- [ ] Flakiness detection (random vs deterministic failures)
- [ ] Early-warning signals (predict failure before it completes)

## License

MIT

## Questions?

This project is built as a production-ready portfolio piece and genuine learning tool for AI reliability engineering roles.

For questions or suggestions, open an issue or submit a PR.

---

**Built with:** Python · LangGraph · Pydantic · pytest
