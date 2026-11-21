# Article 15 lab — Evaluation, Observability & Deployment

## Scope

This is an **offline teaching lab**, not an installed Voice Agent, not a deployed STT/LLM/TTS pipeline, and not a security or compliance certification. All traces are synthetic.

## Prerequisites

Python 3.11+; no pip installation required. Docker + Docker Compose are **optional**.

## Run

From the `Voice-Agent-Series` root:

```bash
python -m unittest discover -s examples -p 'test_voice_eval_observability_lab.py' -v
python examples/voice_eval_observability_lab.py --group baseline --report examples/15-baseline-report.json
python examples/voice_eval_observability_lab.py --group regression --min-samples 5 --report examples/15-regression-report.json
```

The regression command is **expected to exit with code 2**, because the deliberately bad cases should block release.

## Optional local diagnostics server

```bash
cd examples/15-deployment-demo
python health_demo.py
curl -fsS http://127.0.0.1:8105/health/live
curl -fsS http://127.0.0.1:8105/health/ready
curl -fsS http://127.0.0.1:8105/metrics
```

Default host binding is localhost. It checks only its own process, not real STT/LLM/TTS providers, audio streams, queue workers, database, or TURN. It must not be called a production agent health check.

## Optional Docker

```bash
cd examples/15-deployment-demo
docker compose up --build -d
docker compose ps
curl -fsS http://127.0.0.1:8105/health/ready
docker compose down
```

Docker is *not* executed during the offline unit-test suite. The sample compose file binds only to host `127.0.0.1`. The workflow file is a sample for a repository containing the `examples/` folder; review and pin third-party actions to trusted SHAs before using it.

## Illustrative release gates

- At least 20 cases and interruption coverage.
- Intent/tool exact-match rate >= 95%.
- P95 first-played-audio latency <= 1800 ms.
- P95 interruption stop latency <= 250 ms.
- Exactly zero unauthorized or unsafe writes.
- Exactly zero privacy leak flags.

The thresholds are **pedagogical sample values**; set appropriate ones based on user research, real baseline distributions, and risk assessment. A passing *synthetic* gate does not prove readiness.

## Important safeguards

No raw recordings, identifiable transcripts, prompts, API keys, or access tokens belong in the sample event logs. For real production, add end-to-end auth, scoped secrets, provider dependency checks, distributed tracing with protected sampling/retention, user consent and data policies, dashboards/alerting, real network and load testing, protected CI secrets, rollback strategy, and measured SLOs.
