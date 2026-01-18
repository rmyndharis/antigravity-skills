# Security Policy

This repository ships skills that may recommend terminal commands or infrastructure changes. Keep safety in mind when authoring or updating skills.

## Authoring Guidelines

- Require explicit confirmation before destructive actions (for example: rm -rf, kubectl delete, terraform apply).
- Prefer read-only, plan, or dry-run commands before any write operation.
- Avoid embedding secrets, tokens, or credentials in examples. Use placeholders.
- Add a "Safety" section in SKILL.md for any skill that touches production, infrastructure, or data.
- Default to least-privilege guidance and highlight rollback steps when relevant.

## Reporting

If you discover a security issue in this repository, please open an issue with details and reproduction steps.
