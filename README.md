# Congestion Pricing Monitor

Causal analysis of NYC's January 2025 congestion pricing program.
Estimates the causal effect on traffic speed, transit ridership, and
air quality using difference-in-differences and synthetic control.

## Status

Pre-registered analysis plan: see `docs/pre_registration.md`.
Last data refresh: see dashboard.

## Quickstart

```bash
git clone <repo>
cd congestion-pricing-monitor
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
make data        # pull and validate all sources
make analysis    # run DiD and synthetic control
make dashboard   # launch Streamlit locally
```

## Project structure

See `docs/decisions/0001-project-layout.md` for the rationale.

## Methodology

This is a causal inference project, not a predictive one.
Pre-registration is binding: any deviation from the plan is logged
in `docs/decisions/` with a dated rationale.