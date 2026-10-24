# Brightloop — Product Overview

Brightloop is a webhook delivery and API orchestration platform. It sits between your upstream event sources (payment processors, CRMs, IoT devices, third-party SaaS) and your internal services, ensuring every event is delivered reliably, in order, and with full observability.

## Core Features

**Reliable Webhook Delivery**
Brightloop guarantees at-least-once delivery with configurable retry logic. Exponential backoff, dead-letter queues, and per-endpoint circuit breakers are built in — no configuration required to get started.

**Event Fan-out**
One inbound event can be forwarded to multiple downstream endpoints simultaneously. Each destination gets its own delivery guarantee and retry budget.

**Real-time Dashboard**
The Brightloop dashboard shows live event throughput, per-endpoint success rates, latency percentiles, and delivery failures — all without leaving the platform.

**Webhook Signatures**
All outbound webhooks are signed with HMAC-SHA256. Receiving services can verify authenticity without managing certificates.

**Replay and Backfill**
Any event can be replayed on demand, up to 30 days back. Useful for recovering from downstream outages without re-triggering upstream sources.

**Transformations**
Lightweight payload transformations (field mapping, filtering, enrichment) can be applied per destination without deploying new code.

## Supported Languages and SDKs

Official SDKs are available for: Python, Node.js/TypeScript, Go, Ruby, and Java. The REST API works with any language.

## Integrations

Brightloop has native integrations with: payment processors, CRMs, source-control hosts, incident-management and monitoring tools, chat platforms, and 60+ other services. Custom integrations are supported via the REST API.
