# 51CTO Platform Profile

Platform ID: `51cto`

## Position

- Purpose: operationally useful enterprise IT, infrastructure, deployment, and troubleshooting guidance.
- Reader intent: execute a change safely, diagnose a system, or understand an operational tradeoff.
- Best fit: servers, networks, cloud, databases, security, deployment, observability, and operations.

## Write

- Title: name the system, operational task or failure, and the verified outcome.
- Opening: state the topology or environment, business or operational impact, and change boundary.
- Structure: prerequisites, current state, risk assessment, procedure, verification, rollback, and troubleshooting.
- Voice: operational, cautious, and explicit about privileges, scope, and blast radius.
- Depth: retain versions, commands, configuration, service dependencies, backups, monitoring, and recovery steps.
- Links: prefer vendor documentation, standards, and authoritative security guidance.
- Ending: provide a concise runbook or pre-change checklist.

## Visuals

- Use topology diagrams, monitoring views, terminal output, configuration diffs, and before-and-after system state.
- Redact hostnames, addresses, credentials, account identifiers, and internal infrastructure details.

## Avoid

- Production commands without safety context, irreversible steps without rollback, guessed capacity claims, and exposing real infrastructure.
- Treating a lab result as production proof.

## Platform QA

- Verify prerequisites, privilege level, backup, order of operations, validation, rollback, and security implications.
- Confirm every command and configuration fragment matches the stated environment.
