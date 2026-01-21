---
name: Review Branch
description: Code review, security audit, architecture review
---

# Review Skills

## Sub-Skills
- `code/` - PR reviews, code quality
- `security/` - Vulnerability scanning, secrets detection
- `architecture/` - Design review, pattern compliance

---

## Code Review Checklist

### Correctness
- [ ] Logic is correct and handles edge cases
- [ ] Error handling is complete (no silent failures)
- [ ] Async operations properly awaited
- [ ] Resource cleanup (connections, file handles)

### Type Safety
- [ ] No `any` types in TypeScript
- [ ] Pydantic models for all API boundaries
- [ ] Type hints on all Python functions

### Security
- [ ] No hardcoded secrets or API keys
- [ ] Input validation on all user data
- [ ] SQL injection protection (parameterized queries)
- [ ] XSS protection (sanitized outputs)

### Testing
- [ ] New code has tests
- [ ] Tests cover happy path and error cases
- [ ] Mock patterns follow standards

### Maintainability
- [ ] Code follows naming conventions
- [ ] Functions are focused (single responsibility)
- [ ] No magic numbers (use constants)
- [ ] Comments explain "why", not "what"

---

## Security Audit Checklist (OWASP-Aligned)

### A01: Broken Access Control
- [ ] Authorization checks on all endpoints
- [ ] Role-based access control enforced
- [ ] No direct object references exposed

### A02: Cryptographic Failures
- [ ] Sensitive data encrypted at rest
- [ ] TLS for data in transit
- [ ] No MD5/SHA1 for passwords

### A03: Injection
- [ ] Parameterized database queries
- [ ] Command injection prevention
- [ ] Safe file path handling

### A05: Security Misconfiguration
- [ ] No default credentials
- [ ] Debug mode disabled in production
- [ ] CORS properly configured

### A07: Authentication Failures
- [ ] Strong password requirements
- [ ] Rate limiting on login
- [ ] Session timeout implemented

---

## Architecture Review Protocol

### Pattern Compliance
- [ ] Domain isolation respected (no cross-imports)
- [ ] Schema-first design followed
- [ ] Router pattern for FastAPI
- [ ] Error Boundaries in React

### Performance
- [ ] N+1 query patterns avoided
- [ ] Pagination on list endpoints
- [ ] Caching for expensive operations

### Scalability
- [ ] Stateless services
- [ ] Database connections pooled
- [ ] Background tasks for long operations

---

## Review Output Format

```markdown
## Summary
Brief overview of what was reviewed.

## Findings

### Critical
- [Issue]: [Location] - [Impact]

### High
- [Issue]: [Location] - [Impact]

### Medium
- [Issue]: [Location] - [Impact]

### Low
- [Issue]: [Location] - [Impact]

## Recommendations
1. [Action item]
2. [Action item]
```
