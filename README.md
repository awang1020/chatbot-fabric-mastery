# Chatbot Fabric Mastery — RAG Chatbot

Production-ready Retrieval-Augmented Generation chatbot that answers
Microsoft Fabric and Power BI questions **strictly** from the
[Fabric Mastery newsletter](https://blog.antoinewang-tech.com/) archive.
No hallucination, every answer cited with a direct link to the source
edition.

**Landing page (indexable):** <https://awang1020.github.io/chatbot-fabric-mastery/>
**Live app:** <https://chat.antoinewang-tech.com>
**Repo:** <https://github.com/awang1020/chatbot-fabric-mastery>

Acquisition runs on the public landing page, the newsletter and GitHub;
the chatbot itself is the retention product. Visitors get a code-free demo,
then unlock unlimited questions with the reader code published in the
newsletter.

| Concern         | Choice |
| --------------- | ------ |
| LLM + embeddings | Azure OpenAI (`gpt-4o-mini` + `text-embedding-3-small`), Entra ID auth, no API keys |
| Orchestration   | LlamaIndex `ContextChatEngine` |
| Vector store    | ChromaDB persistent collection, baked into the image |
| UI              | Streamlit (Apple-style theme), EN/FR |
| Hosting         | Azure Container Apps, scale-to-zero, system-assigned managed identity |
| Container image | GitHub Container Registry (GHCR), built weekly by GitHub Actions |
| CI/CD           | GitHub Actions + OIDC federated identity (no long-lived secrets) |
| Cost ceiling    | Hard AOAI TPM cap (chat 10K, embed 30K) + Azure budget 20 €/mo with email alerts |
| Anti-abuse      | Freemium gate (free demo questions, then the reader code published in the newsletter), strict-RAG prompt + regex jailbreak detector + per-session sliding rate limit |

---

## Table of contents

1. [Architecture](#1-architecture)
2. [Repository layout](#2-repository-layout)
3. [Local development](#3-local-development)
4. [One-time Azure setup](#4-one-time-azure-setup)
5. [One-time GitHub setup](#5-one-time-github-setup)
6. [Deploy infrastructure](#6-deploy-infrastructure)
7. [Freemium access + guardrails](#7-freemium-access--prompt-level-guardrails)
8. [Trigger the CI/CD pipeline](#8-trigger-the-cicd-pipeline)
9. [Operating in production](#9-operating-in-production)
10. [Security posture](#10-security-posture)
11. [Cost controls](#11-cost-controls)
12. [Troubleshooting](#12-troubleshooting)
13. [Renaming the project](#13-renaming-the-project)

---

## 1. Architecture

```mermaid
flowchart LR
    subgraph "GitHub"
        REPO[Repo: awang1020/chatbot-fabric-mastery]
        PAGES[GitHub Pages<br/>public landing page<br/>docs/]
        GHA[GitHub Actions<br/>Weekly cron + push]
        GHCR[GHCR public image<br/>ghcr.io/awang1020/ask-fabric-mastery/ask-fabric-mastery]
    end

    subgraph "Azure subscription"
        subgraph "rg-ask-fabric-mastery (Sweden Central)"
            AOAI[Azure OpenAI<br/>oai-fabmastery-rdeaxiqrltzqo<br/>gpt-4o-mini + embedding-3-small]
            ACA[Container App<br/>ask-fabric-mastery<br/>scale 0-2, port 8501]
            ENV[Container Apps Env<br/>cae-ask-fabric-mastery]
            LAW[Log Analytics<br/>law-ask-fabric-mastery]
            BUDGET[Azure Budget 20 EUR/mo]
        end
        ENTRA[Entra ID<br/>SP gha-ask-fabric-mastery]
    end

    USER[Newsletter subscriber] -->|HTTPS + access code| ACA
    VISITOR[Search / LinkedIn visitor] -->|indexable content| PAGES
    PAGES -->|CTA| ACA
    REPO -->|cron 09:30 UTC Tue<br/>or push to main| GHA
    GHA -->|OIDC token| ENTRA
    GHA -->|docker push| GHCR
    GHA -->|az containerapp update| ACA
    ACA -->|managed identity| AOAI
    ACA -->|stdout/stderr| LAW
    ACA -->|pull image| GHCR
    BUDGET -.->|alert email| USER
```

### Request flow

1. Visitor lands on the Container App URL → Streamlit shows the hero and the
   example prompts, with no code required.
2. Visitor asks up to `FREE_QUESTIONS` demo questions. When the quota runs
   out, the unlock panel replaces the composer and points at the newsletter.
3. Visitor pastes the reader code → session marker stored in
   `st.session_state` (no cookie sent anywhere else) → unlimited questions.
4. Every question also passes the in-app **rate limiter**
   (`RATE_LIMIT_MAX_QUESTIONS` in `RATE_LIMIT_WINDOW_SECONDS`).
5. LlamaIndex retrieves the top-K chunks from the local Chroma collection
   (no network call).
6. Azure OpenAI embedding + chat are called over Entra ID (managed identity,
   no key).
7. Answer + source cards (title, date, score, snippet, direct Substack link)
   are rendered.

### Why this stack

- **No hallucination** — `ContextChatEngine` is wrapped by a strict system prompt that refuses to answer when retrieval is empty.
- **Self-contained image** — the Chroma index ships in the Docker image; pods start cold without any external storage.
- **Scale to zero** — no idle cost.
- **OIDC** — GitHub Actions never holds a long-lived Azure secret.
- **Hard cost ceiling** — capacity TPM limits + Azure budget make blowups financially impossible.

---

## 2. Repository layout

```
.
├── app.py                       # Streamlit UI (auth gate, rate limit, chat)
├── Dockerfile                   # Self-contained image (data + index baked in)
├── .dockerignore
├── .streamlit/config.toml       # Theme + telemetry off
├── .env.example                 # Local config template
├── requirements.txt
│
├── assets/                      # Static brand assets (logo, future favicons)
│   └── logo_substack.webp
│
├── src/
│   ├── config.py                # pydantic-settings (env-driven)
│   ├── models.py                # AzureOpenAI LLM + Embedding (Entra ID)
│   ├── indexer.py               # Loaders + Chroma collection
│   ├── chat_engine.py           # ContextChatEngine + enriched Source dataclass
│   ├── prompts.py               # Strict no-hallucination system prompt
│   ├── retriever.py             # Wrapper around VectorIndexRetriever
│   ├── safety.py                # Password gate + per-session rate limit
│   └── i18n.py                  # EN/FR translations
│
├── scripts/
│   ├── ingest_substack.py       # Substack archive → Markdown (browser UA + 403 fallback)
│   ├── build_index.py           # Chroma index builder
│   ├── deploy_azure.ps1         # One-shot RG + AOAI deploy
│   └── setup_github_oidc.ps1    # Bootstrap SP + federated cred + RBAC
│
├── docs/                        # GitHub Pages: public indexable landing page
│   ├── index.html               # Use cases, demo, FAQ, OG + JSON-LD
│   ├── robots.txt
│   └── sitemap.xml
│
├── infra/
│   ├── main.bicep               # Subscription-scope: RG + AOAI module
│   ├── main.bicepparam
│   ├── openai.bicep             # AOAI account + 2 deployments
│   ├── app.bicep                # LAW + ACA Env + Container App + RBAC
│   └── budget.json              # 20 EUR/mo with email alerts
│
├── .github/workflows/refresh.yml  # Weekly ingest -> embed -> build -> push -> deploy
│
├── data/newsletters/            # 23 markdowns + _sources_index.json (committed)
└── storage/chroma/              # 86-chunk Chroma collection (NOT committed)
```

---

## 3. Local development

### Prerequisites

| Tool       | Version | Install hint |
| ---------- | ------- | ------------ |
| Python     | 3.11+   | <https://www.python.org/> |
| Azure CLI  | 2.60+   | `winget install Microsoft.AzureCLI` |
| GitHub CLI | 2.40+   | `winget install GitHub.cli` |
| PowerShell | 7+      | `winget install Microsoft.PowerShell` |
| Docker     | optional | only needed to build/test the image locally |

### Setup

```powershell
git clone https://github.com/awang1020/chatbot-fabric-mastery.git
cd chatbot-fabric-mastery
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt

az login
az account set --subscription <YOUR_SUB_ID>

Copy-Item .env.example .env
# Edit .env — at minimum:
#   AZURE_OPENAI_ENDPOINT=...
#   AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
#   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small

# Optional: cache new posts from the newsletter (the repo already ships 23 of them)
python -m scripts.ingest_substack --skip-paywalled --delay 0.4

# Build the Chroma index (one-shot; ~30 sec for 23 posts)
python -m scripts.build_index --rebuild

# Run the UI
streamlit run app.py
```

The first AOAI call will use your `az login` identity, so make sure you have
the **Cognitive Services OpenAI User** role on the AOAI account.

### Local auth + rate-limit testing

```powershell
$env:APP_PASSWORD = "test1234"
$env:RATE_LIMIT_MAX_QUESTIONS = "3"
$env:RATE_LIMIT_WINDOW_SECONDS = "60"
streamlit run app.py
```

---

## 4. One-time Azure setup

The AOAI account + 2 deployments are provisioned by `infra/main.bicep`.

```powershell
# Register required providers (idempotent)
az provider register -n Microsoft.App --wait
az provider register -n Microsoft.OperationalInsights --wait
az provider register -n Microsoft.CognitiveServices --wait

# Subscription-scope deploy: creates rg + AOAI + deployments
az deployment sub create `
  --location swedencentral `
  --template-file infra/main.bicep `
  --parameters infra/main.bicepparam
```

Outputs include the AOAI account name (`oai-fabmastery-rdeaxiqrltzqo` in this
repo). All later commands reference that name.

> **Region note.** Sweden Central was picked because `text-embedding-3-small`
> requires `GlobalStandard` SKU there. If you change regions, double-check
> the SKU availability table.

> **Tenant note.** The tenant used here enforces `disableLocalAuth=true`,
> so no API key is ever issued. All code paths use Entra ID via
> `ChainedTokenCredential(AzureCliCredential, EnvironmentCredential,
> ManagedIdentityCredential)`.

---

## 5. One-time GitHub setup

### a) Create the repo

```powershell
gh repo create <OWNER>/<REPO> --public --source . --remote origin --push
```

### b) Bootstrap OIDC (least-privilege SP + federated trust)

```powershell
pwsh ./scripts/setup_github_oidc.ps1 `
  -GithubOwner <OWNER> `
  -GithubRepo  <REPO> `
  -OpenAiName  oai-fabmastery-rdeaxiqrltzqo
```

This script:
- Creates an Entra ID app registration + service principal (idempotent).
- Adds **one** federated credential bound to `refs/heads/main`
  (we intentionally do **not** create a `pull_request` one because on a
  public repo it would let any fork PR mint a token).
- Grants the SP **Cognitive Services OpenAI User** on the AOAI account.
- Prints all secrets/variables to set on the repo.

### c) Tighten the SP scope (after the first deploy)

Once the Container App exists, downgrade the SP from Contributor to the
least-privilege role that can update images:

```powershell
$spId = az ad sp list --filter "appId eq '<CLIENT_ID>'" --query "[0].id" -o tsv
$rg   = "/subscriptions/<SUB>/resourceGroups/rg-ask-fabric-mastery"
$app  = "$rg/providers/Microsoft.App/containerapps/ask-fabric-mastery"

az role assignment delete --assignee-object-id $spId --role "Contributor" --scope $rg
az role assignment create --assignee-object-id $spId --assignee-principal-type ServicePrincipal `
  --role "358470bc-b998-42bd-ab17-a7e34c199c0f" --scope $app   # Container Apps Contributor
```

### d) Set the workflow secrets + variables

```powershell
gh secret set AZURE_CLIENT_ID       --body "<from-script-output>"
gh secret set AZURE_TENANT_ID       --body "<from-script-output>"
gh secret set AZURE_SUBSCRIPTION_ID --body "<from-script-output>"

gh variable set AZURE_RESOURCE_GROUP              --body "rg-ask-fabric-mastery"
gh variable set AZURE_CONTAINERAPP_NAME           --body "ask-fabric-mastery"
gh variable set AZURE_OPENAI_ENDPOINT             --body "https://oai-fabmastery-rdeaxiqrltzqo.openai.azure.com/"
gh variable set AZURE_OPENAI_CHAT_DEPLOYMENT      --body "gpt-4o-mini"
gh variable set AZURE_OPENAI_CHAT_MODEL           --body "gpt-4o-mini"
gh variable set AZURE_OPENAI_EMBEDDING_DEPLOYMENT --body "text-embedding-3-small"
gh variable set AZURE_OPENAI_EMBEDDING_MODEL      --body "text-embedding-3-small"
```

---

## 6. Deploy infrastructure

The Container App + Log Analytics + Env + role assignment all live in `infra/app.bicep`.

```powershell
az deployment group create `
  --resource-group rg-ask-fabric-mastery `
  --template-file infra/app.bicep `
  --parameters openAiName=oai-fabmastery-rdeaxiqrltzqo `
  --query "{appUrl: properties.outputs.appUrl.value}" -o json
```

The first deploy uses a placeholder image (`mcr.microsoft.com/k8se/quickstart`)
on purpose; the GHA workflow replaces it with the real GHCR image on the
first run.

### Apply the cost guardrail

```powershell
# 1) Cap absolute AOAI throughput
az cognitiveservices account deployment create `
  -g rg-ask-fabric-mastery -n oai-fabmastery-rdeaxiqrltzqo `
  --deployment-name gpt-4o-mini --model-name gpt-4o-mini `
  --model-version "2024-07-18" --model-format OpenAI `
  --sku-name GlobalStandard --sku-capacity 10        # 10K TPM

az cognitiveservices account deployment create `
  -g rg-ask-fabric-mastery -n oai-fabmastery-rdeaxiqrltzqo `
  --deployment-name text-embedding-3-small --model-name text-embedding-3-small `
  --model-version "1" --model-format OpenAI `
  --sku-name GlobalStandard --sku-capacity 30        # 30K TPM

# 2) Subscription-level monthly budget on this RG
az rest --method PUT `
  --url "https://management.azure.com/subscriptions/<SUB>/providers/Microsoft.Consumption/budgets/budget-ask-fabric-mastery?api-version=2024-08-01" `
  --body "@infra/budget.json"
```

`infra/budget.json` triggers email alerts at 50%, 80% (actual) and 100%
(forecast).

---

## 7. Freemium access + prompt-level guardrails

The app opens on a **code-free demo**: every visitor can ask `FREE_QUESTIONS`
questions (default 2) and see complete, sourced answers. Once the quota is
spent, an unlock panel asks for the **reader code** you publish at the top of
the latest newsletter edition. Search and social traffic can therefore judge
the product before converting, and the newsletter stays the way to unlock
unlimited use.

The demo quota lives in `st.session_state`, so a fresh browser session resets
it. That is deliberate: it is a conversion nudge, not a security boundary.
The AOAI TPM cap and the Azure budget below remain the real spend ceiling.

Layered defences:

1. **Freemium gate** (`src/safety.py`) reads `APP_PASSWORD` and
   `FREE_QUESTIONS` on the Container App. When `APP_PASSWORD` is unset the
   gate is dormant and the app is fully open (local dev). Constant-time
   comparison avoids trivial timing oracles.
2. **Admin controls are opt-in**: the index rebuild button and the internal
   paths only render when `ADMIN_MODE` is truthy. Never set it on the public
   deployment, since re-embedding the corpus costs AOAI tokens.
3. **Strict-RAG system prompt** (`src/prompts.py`) tells the model to answer
   only from the retrieved excerpts, refuse any out-of-scope topic, and
   ignore every jailbreak / instruction-override attempt.
4. **Regex jailbreak detector** (`src/chat_engine.py::looks_like_jailbreak`)
   short-circuits obvious prompt-injection patterns (`ignore previous
   instructions`, `tu es maintenant`, `DAN`, `developer mode`, `reveal your
   system prompt`, etc.) BEFORE the LLM is called — zero AOAI tokens spent
   on attacks.
5. **Empty-retrieval refusal** when the similarity cutoff filters out every
   chunk: the user gets the refusal line instead of the model speculating.
6. **Per-session sliding rate limit**: 20 questions / 15 min (configurable
   via `RATE_LIMIT_MAX_QUESTIONS` / `RATE_LIMIT_WINDOW_SECONDS`).
7. **AOAI TPM cap**: 10K TPM chat, 30K TPM embedding — hard ceiling on
   throughput regardless of how many users try at once.
7. **Azure budget**: 20 €/month with email alerts at 50 / 80 / 100 %.

### Set or rotate the access code

The image looks at the env var `APP_PASSWORD` at request time. Set it as a
Container Apps **secret** so it never appears in plain text in any template
or log:

```powershell
# Pick a memorable code (publish it in your newsletter)
$pwd = "fabric-mastery-2026"

az containerapp secret set -g rg-ask-fabric-mastery -n ask-fabric-mastery `
  --secrets "app-password=$pwd"

az containerapp update -g rg-ask-fabric-mastery -n ask-fabric-mastery `
  --set-env-vars `
    "APP_PASSWORD=secretref:app-password" `
    "RATE_LIMIT_MAX_QUESTIONS=20" `
    "RATE_LIMIT_WINDOW_SECONDS=900"
```

To rotate the code later, run the two commands again with a new value. Any
open session is invalidated as soon as Streamlit reruns. Open the app to
verify the gate appears before the chat.

---

## 8. Trigger the CI/CD pipeline

```powershell
gh workflow run refresh.yml --repo <OWNER>/<REPO>
```

The workflow:

1. Checks out the repo (which ships the 23 markdown sources + index source files).
2. Runs `scripts.ingest_substack` — if Substack returns 403 to the GitHub
   runner (it does as of writing), the script logs a warning and falls
   back to the committed cache.
3. Runs `scripts.build_index --rebuild` — re-embeds via AOAI under the
   workflow's Entra identity (OIDC).
4. `docker buildx build` → push to GHCR with `:latest` and `:YYYYMMDD-HHMMSS` tags.
5. `az containerapp update` to roll a new revision pointing at the new tag.

A weekly cron at **Tuesday 09:30 UTC** runs the same pipeline so the index
stays current without you doing anything.

---

## 9. Operating in production

### Get the public URL

```powershell
az containerapp show -g rg-ask-fabric-mastery -n ask-fabric-mastery `
  --query properties.configuration.ingress.fqdn -o tsv
```

### Tail container logs

```powershell
az containerapp logs show -g rg-ask-fabric-mastery -n ask-fabric-mastery --tail 100 --follow
```

### Roll back to a previous revision

```powershell
az containerapp revision list -g rg-ask-fabric-mastery -n ask-fabric-mastery -o table
az containerapp revision activate -g rg-ask-fabric-mastery -n ask-fabric-mastery `
  --revision <revision-name>
```

### Force scale-up (kill cold starts while traffic is expected)

```powershell
az containerapp update -g rg-ask-fabric-mastery -n ask-fabric-mastery `
  --min-replicas 1 --max-replicas 3
```

### Rotate the password

```powershell
$pwd = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 24 | ForEach-Object {[char]$_})
az containerapp secret set -g rg-ask-fabric-mastery -n ask-fabric-mastery `
  --secrets "app-password=$pwd"
az containerapp update -g rg-ask-fabric-mastery -n ask-fabric-mastery # restart picks new secret
```

---

## 10. Security posture

| Layer | Control | Status |
| ----- | ------- | ------ |
| Network | HTTPS only (`allowInsecure: false`), TLS managed by ACA | ✅ |
| Network | Public ingress on port 8501 | ⚠ public by design (newsletter audience) |
| Auth (data plane) | AOAI `disableLocalAuth=true` → no API key exists | ✅ |
| Auth (data plane) | Container App talks to AOAI via system-assigned managed identity | ✅ |
| Auth (UI) | Shared access code (published in the newsletter) gates every render | ✅ |
| Prompt safety | Strict-RAG system prompt refuses off-topic + jailbreaks | ✅ |
| Prompt safety | Regex jailbreak detector short-circuits BEFORE LLM call | ✅ |
| Anti-abuse | Per-session sliding-window rate limit (20 questions / 15 min) | ✅ |
| Auth (CI/CD) | GitHub OIDC federated to `refs/heads/main` only (no PR cred) | ✅ |
| RBAC | SP scoped to `Container Apps Contributor` on the app + `Cognitive Services OpenAI User` on AOAI | ✅ |
| Secrets | `.env`, `storage/`, `.vscode/` excluded by `.gitignore` | ✅ |
| Secrets | No long-lived secret on any side (OIDC + managed identity) | ✅ |
| Cost | AOAI capacity capped at 10K TPM chat + 30K TPM embedding | ✅ |
| Cost | Azure Budget 20 €/mo with 3 email alerts | ✅ |
| Image | Self-contained, no runtime download of code or data | ✅ |
| Image | Currently runs as `root` (low risk on a minimal Debian slim) | ⚠ accept |
| Reliability | Single region, single zone (`zoneRedundant: false`) | ⚠ accept |
| Reliability | Liveness + readiness probes on `/_stcore/health` | ✅ |
| Observability | Container logs + console go to Log Analytics | ✅ |
| Observability | No APM / tracing yet (Application Insights not wired) | ⚠ backlog |

### What we explicitly DID NOT enable (and why)

- **Container Apps built-in Entra ID auth.** Would force every visitor into
  your tenant; we want newsletter readers (external users) to access the
  app via a shared code instead.
- **Azure Front Door + WAF.** Adds ~30 €/mo for marginal benefit at this
  scale. The TPM cap + budget already bound the worst-case bill.

---

## 11. Cost controls

### Steady-state monthly bill (low traffic, scale-to-zero)

| Item | Estimate |
| ---- | -------- |
| Container Apps (idle most of the time) | ~0–3 € |
| Log Analytics (1 GB/day cap) | ~2–3 € |
| Azure OpenAI tokens (~1 question per visitor, ~2K tokens) | ~0.5–5 € |
| GHCR storage + bandwidth | 0 € (free for public packages) |
| GitHub Actions minutes (~13 min/run × 4 runs/mo) | 0 € (within free tier) |
| **Total** | **~5–12 €/mo** |

### Hard ceiling (worst-case if someone hammers the password)

- AOAI capacity caps inference rate at ~10K TPM chat → ~30 questions/min
  at 1K-token answers.
- Per-session rate limit caps a *single* visitor at 20 questions / 15 min.
- The Azure budget alerts you at 10/16/20 € absolute.
- If a malicious actor distributes the password, the worst-case sustained
  cost is around 5–10 €/hour for as long as the password stays leaked.
  Rotating the password (Step 9) takes ~30 seconds and immediately stops
  the bleeding.

---

## 12. Troubleshooting

| Symptom | Diagnosis | Fix |
| ------- | --------- | --- |
| `403 Forbidden` on Substack from GitHub runner | Substack rate-limits cloud egress IPs | Workflow already falls back to the committed Markdown cache. Re-ingest locally and push to refresh. |
| `cannot import name 'refresh_sources_index'` in Streamlit | Stale `__pycache__` after a `src/` edit | `Get-ChildItem -Recurse -Directory __pycache__ \| Remove-Item -Recurse -Force` then restart Streamlit. |
| `DefaultAzureCredential` picks Azure Arc and fails | Local dev machine has Azure Arc enrolled | The code uses `ChainedTokenCredential(AzureCli, Env, ManagedIdentity)` — make sure you ran `az login`. |
| `text-embedding-3-small Standard not supported` during deploy | Region/SKU mismatch | Use `GlobalStandard` in Sweden Central (already in the Bicep). |
| Container App returns 502 after a deploy | Image still pulling, or readiness probe failing | `az containerapp revision show ... --query properties.healthState`, then check logs. |
| `gh workflow run` says "the workflow file is invalid" | YAML indentation broken by an editor | Run `gh workflow view refresh.yml` for the parser's exact line/column. |
| App password change not taken into account | Container App not restarted after secret update | `az containerapp update ... --set-env-vars ...` (an env-var rewrite triggers a restart). |

### Useful one-liners

```powershell
# Workflow status of the latest 5 runs
gh run list --repo <OWNER>/<REPO> --limit 5

# Show the failing step's log
gh run view <RUN_ID> --repo <OWNER>/<REPO> --log-failed | Select-String -Pattern "error|Traceback"

# What rights does the GHA SP actually have?
$spId = az ad sp list --filter "appId eq '<CLIENT_ID>'" --query "[0].id" -o tsv
az role assignment list --assignee $spId --all -o table

# Force re-pull a specific image tag
az containerapp update -g rg-ask-fabric-mastery -n ask-fabric-mastery `
  --image ghcr.io/<OWNER>/<REPO>/ask-fabric-mastery:<TAG>
```

---

## 13. Renaming the project

The repo is being renamed `ask-fabric-mastery` -> `chatbot-fabric-mastery`
for brand clarity. The **Azure resource names stay unchanged on purpose**
(`rg-ask-fabric-mastery`, `ask-fabric-mastery`, `cae-…`, `law-…`, the AOAI
account and the managed certificate). Renaming them would mean recreating the
Container App and re-issuing the TLS certificate for
`chat.antoinewang-tech.com` for zero user-visible benefit.

Run the steps in this order — steps 1 and 3 are the ones that break CI if
skipped.

1. **Add the new OIDC federated credential first.** GitHub redirects the repo
   URL after a rename, but it mints OIDC tokens with the **new** name, so the
   existing credential stops matching and `azure/login` fails.

   ```powershell
   pwsh ./scripts/setup_github_oidc.ps1 `
     -GithubOwner awang1020 `
     -GithubRepo  chatbot-fabric-mastery `
     -OpenAiName  oai-fabmastery-rdeaxiqrltzqo
   ```

2. **Rename the repo** in GitHub → Settings → General.

3. **Leave the GHCR package name alone.** The workflow pins the image path to
   `ghcr.io/<owner>/ask-fabric-mastery/ask-fabric-mastery` on purpose. That
   package is already **public**, which is what lets the Container App pull it
   anonymously. Deriving the path from the repo name would push to a brand-new
   package on the first run after the rename, and new GHCR packages default to
   *private* - the revision would then fail to pull. Treat the package like the
   Azure resources: a physical artifact that survives the rebrand.

   After the rename, confirm the workflow can still push to it:
   GitHub -> Packages -> `ask-fabric-mastery` -> Package settings -> Manage
   Actions access, and make sure the renamed repo is listed with `Write`.

4. **Update the local remote.**

   ```powershell
   git remote set-url origin https://github.com/awang1020/chatbot-fabric-mastery.git
   ```

5. **Update the three files that hardcode the public URL.** GitHub Pages is
   already enabled on `main` / `docs`, so the landing page URL changes with the
   repo name. Leaving these pointing at the old name publishes a canonical tag
   aimed at a 404, which is worse for SEO than having no canonical at all.
   Replace `ask-fabric-mastery` with `chatbot-fabric-mastery` in:

   - `docs/index.html` — `rel="canonical"`, `og:url`, `og:image`,
     `twitter:image`, and the "Code source" footer link
   - `docs/sitemap.xml` — `<loc>`
   - `docs/robots.txt` — `Sitemap:`

   Then confirm the new URL actually serves before announcing it anywhere.

6. **Fix the newsletter backlinks.** Several published editions still point at
   `http://awang1020.github.io/ask-fabric-mastery` (old name, plain HTTP).
   Edit the live Substack posts — not just the Markdown copies in
   `data/newsletters/`, which are only the ingestion cache.

7. **Optional but recommended:** create an empty `ask-fabric-mastery` repo
   with a `docs/index.html` that redirects to the new landing page. GitHub
   redirects repository URLs after a rename, but the old
   `github.io/ask-fabric-mastery/` Pages URL is not guaranteed to follow.

8. **Submit the landing page** to Google Search Console and Bing Webmaster
   Tools, and set the GitHub repo `homepage` + topics.

### Verification checklist

```powershell
# CI can still authenticate and deploy
gh workflow run refresh.yml --repo awang1020/chatbot-fabric-mastery
gh run watch --repo awang1020/chatbot-fabric-mastery

# The app is serving the new image and the domain still resolves
az containerapp show -g rg-ask-fabric-mastery -n ask-fabric-mastery `
  --query "{image:properties.template.containers[0].image, fqdn:properties.configuration.ingress.fqdn}"
curl.exe -sS -o NUL -w "%{http_code}`n" https://chat.antoinewang-tech.com/
curl.exe -sS -o NUL -w "%{http_code}`n" https://awang1020.github.io/chatbot-fabric-mastery/
```

If you later move the landing page to a custom domain (for example
`fabric.antoinewang-tech.com`), add `docs/CNAME` and update the URL in
`docs/index.html` (canonical + Open Graph), `docs/sitemap.xml` and
`docs/robots.txt` — those are the only three places that hardcode it.

---

## License

MIT. Newsletter content remains © [Antoine Wang](https://blog.antoinewang-tech.com/).
