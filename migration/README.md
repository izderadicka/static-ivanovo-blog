# Migration workspace

Create these ignored directories when source material is available:

- `source/`: immutable WXR export, uploads, database backup, and baseline capture.
- `work/`: normalized records, conversion staging site, local configuration.
- `reports/`: inventories, URL maps, validation results, and review decisions.

Raw backups may contain private posts, comments, emails, or credentials. Keep them
out of Git and out of `static/` and `content/`. Ignoring files is not a backup:
keep a separate verified copy. Publish only the generated `public/` directory.

See [the migration plan](../docs/migration-plan.md) for the pipeline and gates.
