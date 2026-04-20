# Regression Suite

Safety net for the in-progress refactor. See
`docs/superpowers/specs/2026-04-19-refactor-design.md`.

## Running

```
pytest tests/regression/ -v
```

Expected runtime: under 2 minutes for the fast subset (the default).

Slower, heavier cases are marked `@pytest.mark.slow` and skipped by default.
To include them:

```
pytest tests/regression/ -v  # with slow if you pass -m "slow or not slow"
pytest tests/ -v             # run everything, including slow legacy tests
```

On this repo the full suite (`pytest tests/`) can take 30+ minutes because
`xyz.prepare_state` is expensive for dense n=4+ and for certain sparse
topologies. Run the slow suite on a compute node (slurm), not the headnode.

## Regenerating golden bounds

Only when a phase deliberately changes resource characteristics and the
change is called out in its commit message.

```
python -m tests.regression.generate_bounds
```

This overwrites `tests/regression/golden_bounds.json` with measured CNOT
counts × 1.10 (ceiling). Commit the updated file in the same commit as the
code change that justifies it.
