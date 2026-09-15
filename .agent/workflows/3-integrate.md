---
description: Integrate phase - test adapters with real infrastructure
---

# Phase 3: Integrate (Generic)

## Purpose
Verify that adapter implementations (Databases, Cache, External APIs) interact correctly with real infrastructure.

## Prerequisites
- **Phase 2 (Implement)** completed with unit tests passing.
- Infrastructure (Docker, Staging, etc.) running and accessible.

## When Required
- Any code involving database persistence.
- Integration with external services (APIs, Webhooks).
- Message queues or cache implementations.

## Steps

### 1. Setup Integration Environment
Ensure all required services are running.

```bash
# Example: Ensure services are up
./dc.sh up -d
```

### 2. Integration Testing
Run tests that interact with real services:
- Verify database migrations and schema updates.
- Test real API responses (or use recorded mocks/VCR).

### 3. API Contract Verification
Verify that the frontend and backend contracts are satisfied.
- Check generated API documentation (e.g., Swagger/OpenAPI).
- Run E2E tests if applicable.

### 4. Manual Verification & UX Sync
- Verify behavior under real network/data conditions.
- Ensure loading states and error toasts work as expected.

## Development Commands

> [!NOTE]
> These are placeholder commands. Run `/align-stack` to update them for your project.

```bash
# Run integration tests
./dc.sh exec backend pytest tests/integration
```

## Completion Criteria
- [ ] Integration tests written for all adapters.
- [ ] Environment variables and secrets handled securely.
- [ ] No major regressions in performance or connectivity.

## Next Phase
Proceed to **Phase 4: Verify** (`/4-verify`)
