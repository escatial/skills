# Stage 9: Deploy & Operate

## Persona
**SRE / DevOps**. Move from "works in dev" to "works in prod" with
observability and a rollback path.

## Goal
Produce `09-deploy-plan.md` with:
- Pre-deploy checklist
- Deployment steps (canary strategy)
- Monitoring + alerting
- Rollback runbook
- On-call rotation (if applicable)

## Pre-deploy checklist

- [ ] All migrations reviewed and reversible
- [ ] Secrets managed (env vars, not in repo)
- [ ] TLS certificates ready
- [ ] Database backup taken within last hour
- [ ] Rollback tested in staging
- [ ] On-call aware of deploy window
- [ ] Feature flags in place for risky changes
- [ ] Monitoring dashboard exists for new endpoints

## Deployment strategy

Default: **canary with progressive rollout**:
1. Deploy to canary (5% traffic) — wait 15min, check error rate
2. Promote to 50% — wait 15min, check error rate
3. Promote to 100%

Adjust based on risk:
- Database migration: blue/green or expand/contract (not the
  canary approach, which has dual-write issues)
- Pure code change: canary works
- Big-bang refactor: feature flag, default off, gradual enable

## Database migrations in prod

- **Expand → migrate → contract** pattern:
  1. Deploy code that works with both old and new schema
  2. Run migration that adds the new schema
  3. Backfill data if needed
  4. Deploy code that uses the new schema
  5. Run migration that drops the old schema (in a later release)
- Reason: in-place schema changes during a deploy cause downtime
  and break rolling updates

## Monitoring — the 4 golden signals

Per service:
- **Latency**: P50, P95, P99 for top endpoints
- **Traffic**: requests/sec, by endpoint
- **Errors**: 4xx and 5xx rate, by endpoint
- **Saturation**: CPU, memory, DB connections, queue depth

Plus business-level:
- Signup count
- Order count
- Revenue (if relevant)

## Alerting — what to page on, what to ignore

**Page on**:
- Error rate > 1% sustained 5min
- P95 latency > 2x baseline sustained 5min
- Any 5xx spike
- DB connection pool > 80%
- Disk > 80% or memory > 85%

**Don't page on** (record, but don't wake people):
- Single 4xx (user error)
- Brief blip < 1min
- Planned deploys

## Rollback runbook

Every release must have a tested rollback. Include:
- **Code rollback**: previous image tag, one-command redeploy
- **DB rollback**: reverse migration script (or "no rollback
  possible, forward-fix only" — explicitly call this out)
- **Feature flag kill-switch**: which flag to flip to disable
  the feature without redeploy
- **Data rollback**: rare, painful, but document if the change
  wrote data (e.g. backfill)
- **Communication**: who to notify, what status page to update

## Exit gate
- [ ] Pre-deploy checklist complete
- [ ] Canary 5% → 50% → 100% with no Sev1
- [ ] Monitoring dashboard live and alerting tested
- [ ] Rollback runbook reviewed
- [ ] On-call rotation set
- [ ] Post-mortem template ready (will be needed)

## Common failure modes
- "We'll add monitoring later" — you won't know you have an outage
  until users tweet
- Migrations done in-place during deploy — outage, sometimes data
  loss
- No feature flags for risky changes — must roll back the whole
  release even if only one feature is bad
- Rollback runbook untested — when you need it, it's too late
- "Deploy Friday" without on-call — bad weekends
- No traffic mirroring / shadow testing for big changes — surprises
  in prod
