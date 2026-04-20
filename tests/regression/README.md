# Regression Suite

Safety net for the in-progress refactor. See
`docs/superpowers/specs/2026-04-19-refactor-design.md`.

## Running

```
pytest tests/regression/ -v
```

Expected runtime: under 2 minutes.

## Regenerating golden bounds

Only when a phase deliberately changes resource characteristics and the
change is called out in its commit message.

```
python tests/regression/generate_bounds.py
```

This overwrites `tests/regression/golden_bounds.json` with measured CNOT
counts × 1.10 (ceiling). Commit the updated file in the same commit as the
code change that justifies it.
