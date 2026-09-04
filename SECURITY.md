# Security Policy

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Report privately through
[GitHub Security Advisories](https://github.com/awang1020/chatbot-fabric-mastery/security/advisories/new),
or by replying to any [Fabric Mastery](https://blog.antoinewang-tech.com) newsletter edition.

Expect an acknowledgement within a few days. This is a personal project, so
there is no formal SLA — please allow reasonable time before public disclosure.

## Scope

In scope:

- The Streamlit application (`app.py`, `src/`)
- Container and CI/CD configuration (`Dockerfile`, `.github/workflows/`, `infra/`)
- The public landing page (`docs/`)

Out of scope:

- The Substack newsletter itself (managed by Substack)
- Azure OpenAI and Azure Container Apps platform issues — report those to
  [MSRC](https://msrc.microsoft.com/report)
- Volumetric denial of service. Throughput is deliberately bounded by an Azure
  OpenAI TPM cap and a monthly Azure budget.

## Known and accepted design decisions

These are intentional, not oversights:

- **The reader access code is not a secret.** It is published in a public
  newsletter edition. It exists to add friction and deter bots, not to
  authenticate users.
- **The free-question quota is session-scoped**, so clearing the browser
  session resets it. It is a conversion nudge; the real spend ceilings are the
  Azure OpenAI TPM cap and the Azure budget.
- **Ingress is public by design.** The audience is newsletter readers outside
  the tenant, so tenant-bound Entra authentication is deliberately not used.

## Security posture

- No long-lived credentials exist. The app authenticates to Azure OpenAI with
  a system-assigned managed identity, and CI/CD uses GitHub OIDC federation.
- `disableLocalAuth` is enabled on the Azure OpenAI account, so no API key is
  ever issued.
- Least privilege is enforced: the app identity holds only
  `Cognitive Services OpenAI User` on the Azure OpenAI account; the CI/CD
  principal adds only `Container Apps Contributor` on the container app.
- User questions are never written to logs. Only retrieval metrics are logged.
- Prompt-injection attempts matching known patterns are refused before any
  model call.
