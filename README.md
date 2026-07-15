# Probe

Production reliability evaluator for agentic systems. Stress-test AI agents with intelligent fault injection, LLM-based detection, and adversarial attacks to measure production readiness.

## What Probe Does

Probe systematically evaluates whether your AI agent system is ready for production by:

1. **Injecting 8 types of realistic faults** into your agent
2. **Running intelligent LLM-based detectors** to catch failures
3. **Measuring flakiness** — testing consistency across multiple runs
4. **Testing with adversarial attacks** — intelligent attempts to break your system
5. **Generating a reliability report** with actionable recommendations

## Installation

```bash
pip install probe
export OPENROUTER_API_KEY="your_key_here"
```

Requires Python 3.10+.

## Quick Start

```python
from probe import evaluate
from your_module import YourAgent

agent = YourAgent()
report = evaluate(agent, task="What is the capital of France?")

print(f"Reliability: {report.overall_score}%")
print(f"Production Ready: {report.production_ready}")
print(f"Critical Risks: {report.critical_risks}")
```

## The 8 Fault Types

**Intra-Agent:** Hallucination, Parameter Error, Context Loss, Inexecutable Plan
**Inter-Agent:** Role Ambiguity, Blind Trust, Message Cycle, Instruction Conflict

## Key Features

- **LLM-Based Detection** — Intelligent analysis, not keyword matching
- **Flakiness Analysis** — Measure result consistency
- **Adversarial Testing** — Intelligent breaker agent
- **Real LLM Integration** — Use any OpenRouter model
- **Production Readiness Score** — 0-100 with pass/fail criteria

## Output Example

```json
{
  "overall_reliability_score": 87,
  "production_ready": true,
  "results_per_fault_type": {
    "hallucination": {"detection_rate": 92, "status": "✓ PASS"},
    "role_ambiguity": {"detection_rate": 45, "status": "✗ FAIL"}
  },
  "critical_risks": [
    {"fault_type": "role_ambiguity", "recommendation": "Add role validation"}
  ]
}
```

## API

```python
evaluate(agent, task, model="openai/gpt-3.5-turbo", num_runs=5)
```

Returns: `EvaluationReport` with `overall_score`, `production_ready`, `critical_risks`

## Evaluation Phases

1. **Baseline** — Establish correct behavior
2. **Fault Injection** — Test detection accuracy (8 types × N runs)
3. **Flakiness** — Measure consistency
4. **Adversarial** — Intelligent attacks
5. **Report** — Reliability score + recommendations

## Production Readiness

✅ **PASS** if: Score ≥ 80% AND no fault type below 70% detection

## Supported Models

OpenAI (gpt-4, gpt-4-turbo, gpt-3.5-turbo), Anthropic (claude-3), Mistral

## Testing

```bash
pytest tests/ -v
```

26 tests covering all components.

## Development

```bash
git clone https://github.com/sharifeh-fadaei/probe.git
cd probe
pip install -e .
python main.py
```

## License

MIT

## Author

Sharifeh Fadaei — [GitHub](https://github.com/sharifeh-fadaei)
