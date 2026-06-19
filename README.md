# vorino-content-public

Public slice of the Vorino Ratgeber conveyor.

## Included
- `drafts/`
- `docs/setup-log/` plan + gate snapshots
- `claim-checks/`
- `scripts/content_gate.py`
- `.github/workflows/gate.yml`
- `gate.yml` convenience copy

## Excluded
- `state/wp-state.json`
- private WordPress sync checks/state
- partner CTA target URLs and other private conversion targets

The private repo keeps operational state and partner targets. This repo keeps the public content/control surface only. The private repo keeps the wp-state gate.
