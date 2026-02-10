# Project Status

## Current state summary
- Repository is functionally stable on `main` with `yaml2plot` package and `xarray.Dataset`-based loading.
- Multi-agent role files exist under `agents/roles/`, but canonical workflow state files were previously missing.
- Legacy continuity files exist under `context/` and include outdated/redundant planning items.

## Last merged / verified status
- Latest visible commits on `main` are docs/version updates after xarray migration.
- CI workflows exist for tests/docs/publish; no current evidence of broken workflow config from static inspection.

## Next 1-3 tasks
1. T-001: Complete and validate migration to `agents/context/*` as source of truth.
2. T-002: Implement signal archiving foundation for v2.1.
3. T-003: Add helper signal expression support in YAML specs.

## Known risks / unknowns
- Documentation and narrative context contain stale API references in some places; drift risk remains until actively reconciled.
- Role workflow depends on helper scripts; migration must keep these scripts executable and stable.
- Generated artifacts are tracked in repository tree and can create noisy diffs if not excluded in task-level commits.
