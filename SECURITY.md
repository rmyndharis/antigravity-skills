# Security Policy

This repository ships skills that may recommend terminal commands or infrastructure changes. Keep safety in mind when authoring or updating skills.

## Authoring Guidelines

- Require explicit confirmation before destructive actions (for example: rm -rf, kubectl delete, terraform apply).
- Prefer read-only, plan, or dry-run commands before any write operation.
- Avoid embedding secrets, tokens, or credentials in examples. Use placeholders.
- Add a "Safety" section in SKILL.md for any skill that touches production, infrastructure, or data.
- Default to least-privilege guidance and highlight rollback steps when relevant.

## Reporting

For routine, non-sensitive issues, open a GitHub issue with details and reproduction steps.

For sensitive vulnerabilities (anything that could be exploited before a fix ships), report privately by email to **yudhi@rmyndharis.com** instead of opening a public issue. Include reproduction steps and impact. Please allow a reasonable window for a fix before any public disclosure.
