# RigCheck — Privacy-First PC Component Compatibility Assistant

> **Hacktoberfest DEV Challenge Submission**  
> Powered by local **Gemma 3 4B** vision inference on **Ollama**, secured PC profile storage, responsive **React + TypeScript** drafting UI, and remote access via **Cloudflare Quick Tunnel** and **Render**.

---

## The Problem RigCheck Solves

When shopping for PC hardware—whether standing in a physical retail store, inspecting a box at an electronics market, or browsing a secondhand marketplace—buyers must make quick, high-stakes decisions:
- *Will this graphics card exceed my existing power supply's capacity?*
- *Does this processor fit my motherboard's CPU socket?*
- *Is this board too large for my chassis?*
- *Does this price fit my remaining upgrade budget?*

Existing tools fall short:
- **Desktop Compatibility Tools (e.g., PCPartPicker)**: Require tedious manual searching, typing full part numbers, and navigating complex forms on a desktop screen.
- **Hosted Cloud AI Assistants**: Require uploading photos of private hardware labels to third-party cloud AI vendors, storing data on remote servers without explicit privacy guarantees.

**RigCheck bridges this gap.** You take a photo of a component label or box directly on your phone camera. Your own home PC performs local vision inference using **Gemma 3 4B**, verifies the specs against your saved PC configuration, and returns a verified compatibility breakdown in seconds—while keeping your photos, hardware profile, and inference completely private on your own PC.

---

## System Architecture

RigCheck supports two deployment topologies:

### Topology A: Unified Local Backend & Mobile Quick Tunnel (Default)
In this mode, FastAPI serves the compiled React application and API routes on a single origin over an authenticated Cloudflare Quick Tunnel.

```
 [Mobile Phone / Tablet]
         │
         ▼  (HTTPS over Cellular Data or Wi-Fi)
 [Cloudflare Quick Tunnel: https://<subdomain>.trycloudflare.com]
         │
         ▼  (Proxies strictly port 8000 on loopback)
 ┌─────────────────────────────────────────────────────────────┐
 │ FastAPI Application (127.0.0.1:8000)                        │
 │  ├── Security Headers Middleware (nosniff, DENY, camera)    │
 │  ├── Access Secret Gate & Brute-Force Rate Limiter          │
 │  ├── Session Management (HttpOnly Cookie & Bearer Headers)  │
 │  ├── Static Single-Page App (frontend/dist)                 │
 │  └── API Endpoints (/api/auth, /api/health, /api/profile,   │
 │                     /api/analyze)                           │
 └──────────────────────────────┬──────────────────────────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        ▼ (Loopback 127.0.0.1 only)                     ▼ (Host PC Filesystem)
 ┌──────────────────────────────────────┐        ┌──────────────────────┐
 │ Ollama (gemma3:4b) @ 127.0.0.1:11434 │        │ Local Profile JSON   │
 │ (Never exposed to tunnel/internet)   │        │ data/user_profile.js │
 └──────────────────────────────────────┘        └──────────────────────┘
```

### Topology B: Render Static Site + Cloudflare Tunnel Backend (Decoupled)
In this mode, the frontend is deployed as a high-performance static website on Render (`https://rigcheck-frontend.onrender.com`), connecting cross-origin to your PC's authenticated Cloudflare Tunnel endpoint.

```
 [Mobile Phone Browser]
      │                      │
      │ 1. Loads Static SPA  │ 2. Authenticated Cross-Origin API
      ▼                      ▼
 ┌──────────────────┐    ┌──────────────────────────────────────────────┐
 │ Render Static    │    │ Cloudflare Quick Tunnel                      │
 │ Site CDN         │    │ (https://<tunnel-id>.trycloudflare.com)      │
 │ (frontend/dist)  │    └──────────────────────┬───────────────────────┘
 └──────────────────┘                           │
                                                ▼
                                 ┌─────────────────────────────┐
                                 │ Local PC FastAPI (port 8000)│
                                 │ Ollama + Private Profile    │
                                 └─────────────────────────────┘
```

---

## Key Features & Supported Compatibility Checks

### 1. Zero-Cloud Local Vision Inference
- Powered by **Google Gemma 3 4B** running locally on your PC via **Ollama**.
- Structured system prompting extracts brand, model, series, TDP, recommended PSU wattage, socket, form factor, and visible packaging labels.
- **Uncertainty Preservation**: If a parameter (e.g., TDP or clearance) is not visible or clear, the model returns `null` and marks it in `unresolved_fields`. RigCheck never invents or hallucinates hardware specifications.

### 2. Optional SerpAPI Technical Reference Search
- When a component is positively identified by model number but critical electrical or physical ratings are omitted from the retail packaging, RigCheck can optionally query **SerpAPI** for technical specification sheets.
- Only technical hardware identifiers (e.g. `ASUS Dual RTX 4070 OC specs TDP PSU`) are queried.
- **Privacy Assurance**: Component photos, user profile data, and IP addresses are never transmitted to search services. All API credentials remain server-side in `.env`.

### 3. Verified Compatibility Engine
RigCheck evaluates hardware rules deterministically and outputs a 3-state verdict:
- **Compatible (PASS)**: Verified to work within electrical and physical boundaries.
- **Needs Verification (UNKNOWN / WARN)**: Inconclusive data or minor constraints detected (e.g., missing label spec or budget exceeded).
- **Incompatible (FAIL)**: Definite physical or electrical mismatch.

| Check Category | Evaluation Logic | Verdict States |
|---|---|---|
| **PSU Wattage Capacity** | Compares user's installed power supply wattage against recommended GPU/system requirements | `PASS` (PSU ≥ Req), `FAIL` (PSU < Req), `UNKNOWN` (Spec missing) |
| **CPU / Motherboard Socket** | Evaluates CPU socket compatibility (e.g. AM5, AM4, LGA1700, LGA1851) | `PASS` (Match), `FAIL` (Mismatch), `UNKNOWN` (Spec missing) |
| **Form Factor Clearance** | Compares motherboard & component form factors (ATX, Micro-ATX, Mini-ITX) | `PASS` (Compatible), `FAIL` (Incompatible), `UNKNOWN` |
| **Budget Constraint (IDR)** | Compares component market price in Indonesian Rupiah against configured ceiling | `PASS` (≤ Budget), `WARN` (> Budget) |

### 4. Robust Remote Security & Access Control
- **Access Secret Gate**: All protected endpoints (`/api/profile`, `/api/analyze`, detailed telemetry) require an `ACCESS_SECRET`.
- **Constant-Time Verification**: Prevents timing attacks using `secrets.compare_digest`.
- **Brute-Force Rate Limiter**: Client IP is locked out for 30 seconds after 5 consecutive failed attempts (HTTP 429).
- **Dual Authentication Transport**: Supports `HttpOnly` cookies (`SameSite=None` over HTTPS) and `Authorization: Bearer <token>` / `X-RigCheck-Token` headers for seamless cross-origin mobile operation.
- **Private Binding**: Ollama is bound strictly to `127.0.0.1:11434` and never forwarded through the tunnel.
- **Zero Image Persistence**: Uploaded images are held strictly in memory as temporary buffers for inference and immediately discarded. No images are saved to disk.
- **Directory Protection**: Private files (`.env`, `data/user_profile.json`) are blocked from static file exposure.

---

## Directory Structure

```
/home/axel/Development/RigCheck/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration settings, access secret, session TTL & lockout
│   ├── dependencies.py        # Token extraction (Cookie, Bearer, X-RigCheck-Token) & auth guards
│   ├── main.py                # Security headers, CORS regex (tunnel & Render), SPA mount
│   ├── models/
│   │   ├── analysis.py        # Vision extraction & search enrichment Pydantic schemas
│   │   ├── compatibility.py   # Compatibility reports, check items, 3-state verdicts
│   │   └── profile.py         # User PC hardware profile schema
│   ├── routers/
│   │   ├── analyze.py         # POST /api/analyze (Image upload & compatibility evaluation)
│   │   ├── auth.py            # POST /api/auth/login, logout, GET /status
│   │   ├── health.py          # GET /api/health (Sanitized when unauthenticated)
│   │   └── profile.py         # GET & PUT /api/profile (User rig configuration)
│   └── services/
│       ├── auth_service.py    # Rate limiter, constant-time checks, in-memory TTL sessions
│       ├── compatibility.py   # Rule evaluation engine
│       ├── ollama_client.py   # Gemma 3 4B vision extraction with uncertainty audit
│       ├── profile_storage.py # Local JSON atomic file storage
│       └── search_service.py  # SerpAPI technical specifications lookup
├── frontend/                  # React 19 + TypeScript + Vite SPA
│   ├── src/
│   │   ├── components/        # AuthModal, Header, ScannerView, ResultsView, ProfileView, HistoryView
│   │   ├── services/api.ts    # Configurable API client with cross-origin credentials & token handling
│   │   ├── types/             # TypeScript interfaces mirroring backend models
│   │   └── App.tsx            # Application lifecycle & station locking
│   └── dist/                  # Production build output
├── tests/                     # 31 Automated pytest tests
│   ├── test_analyze_endpoint.py
│   ├── test_auth.py           # Login, rate limiting, logout, and CORS preflight tests
│   ├── test_compatibility.py   # PSU, socket, form factor, and budget test cases
│   ├── test_health.py         # Authenticated vs unauthenticated telemetry
│   ├── test_image_validation.py # MIME, empty, and file size constraints
│   ├── test_ollama_parser.py  # JSON repair & uncertainty audit tests
│   └── test_profile.py        # Storage persistence and validation tests
├── data/
│   └── .gitkeep               # Preserves data directory structure (profile JSON is gitignored)
├── .env.example               # Template environment configuration (no secrets)
├── .gitignore                 # Excludes .env, local JSON profiles, node_modules, and dist
├── package.json               # Root monorepo script helper (build, lint)
├── pyproject.toml             # Python dependencies and pytest configuration
├── render.yaml                # Infrastructure-as-Code Blueprint for Render static site
├── requirements.txt           # Python dependency manifest
└── README.md
```

---

## Environment Variables

Configure your local `.env` file (copied from `.env.example`). **Never commit `.env` to Git.**

| Variable | Default | Description |
|---|---|---|
| `HOST` | `127.0.0.1` | Local host interface (always keep 127.0.0.1) |
| `PORT` | `8000` | Application port |
| `DEBUG` | `false` | FastAPI debug mode |
| `ACCESS_SECRET` | *(Random if empty)* | Strong secret required to unlock the station on your phone |
| `SESSION_TTL_HOURS` | `24` | Session lifetime before re-authentication is required |
| `MAX_FAILED_AUTH_ATTEMPTS` | `5` | Maximum failed attempts before temporary lockout |
| `AUTH_LOCKOUT_SECONDS` | `30` | Duration of brute-force lockout in seconds |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Ollama local endpoint |
| `OLLAMA_MODEL` | `gemma3:4b` | Installed local vision model |
| `SERPAPI_API_KEY` | `""` | Optional SerpAPI key for missing technical spec lookups |
| `SERPAPI_ENABLED` | `true` | Toggle external search fallback |
| `PROFILE_STORAGE_PATH` | `data/user_profile.json` | Local path for saved PC profile |
| `MAX_UPLOAD_SIZE_BYTES` | `10485760` (10 MB) | Maximum upload file size |

---

## Local Setup & Quick Start

### 1. Prerequisites
- Python 3.11+
- Node.js 20+ & npm
- [Ollama](https://ollama.ai) with `gemma3:4b` installed (`ollama pull gemma3:4b`)
- [Cloudflare Tunnel CLI (`cloudflared`)](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)

### 2. Backend Installation
```bash
cd /home/axel/Development/RigCheck
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and configure your ACCESS_SECRET
```

### 3. Frontend Build
```bash
cd /home/axel/Development/RigCheck/frontend
npm install
npm run build
```

### 4. Running the Complete Application
In Terminal 1 (Ollama):
```bash
ollama serve
```

In Terminal 2 (FastAPI Backend + Frontend SPA):
```bash
cd /home/axel/Development/RigCheck
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open your browser at `http://127.0.0.1:8000` to access the application locally.

---

## Secure Remote Phone Access (Cloudflare Quick Tunnel)

Cloudflare Quick Tunnels provide instant, ephemeral HTTPS endpoints without requiring router port forwarding or DNS setup.

### 1. Install `cloudflared` (if not present)
```bash
mkdir -p ~/.local/bin
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o ~/.local/bin/cloudflared
chmod +x ~/.local/bin/cloudflared
```
*(Ensure `~/.local/bin` is in your `$PATH`)*.

### 2. Start the Tunnel
```bash
cloudflared tunnel --url http://127.0.0.1:8000
```
`cloudflared` will generate a public URL:
```text
https://<random-subdomain>.trycloudflare.com
```

### 3. Access on Mobile Phone
1. On your phone (over cellular 4G/5G or Wi-Fi), open the `https://<random-subdomain>.trycloudflare.com` URL.
2. The **Hardware Station Locked** screen will appear.
3. Enter your configured `ACCESS_SECRET` and tap **Unlock Station**.
4. You now have full access to your PC configuration, camera scanner, and compatibility engine.

### 4. Shutting Down
Press `Ctrl+C` in the `cloudflared` terminal. The public URL is immediately dismantled.

---

## Deploying Frontend as a Static Site on Render

You can also host the frontend on Render while keeping the backend and Ollama on your PC.

### 1. Render Static Site Settings
- **Repository**: Connected to your GitHub repository (`RigCheck`).
- **Runtime**: Static Site.
- **Build Command**: `cd frontend && npm install && npm run build` (or root `npm run build`).
- **Publish Directory**: `frontend/dist`.
- **Environment Variables**:
  - `VITE_API_BASE_URL`: *(Optional)* Set to your active Cloudflare Tunnel URL (e.g., `https://xyz.trycloudflare.com`).

*(Or simply deploy using the included `render.yaml` Blueprint file)*.

### 2. Connecting Render to Your Local Backend
1. Open your Render site (e.g. `https://rigcheck-frontend.onrender.com`) on your phone or PC.
2. On the **Hardware Station Locked** modal, tap **Configure Backend Tunnel URL**.
3. Paste your active Cloudflare Tunnel URL (e.g. `https://xyz.trycloudflare.com`).
4. Enter your `ACCESS_SECRET` and tap **Unlock Station**.
5. The frontend will communicate securely with your local PC backend across origins using CORS and Bearer tokens.

---

## Automated Testing & Quality Assurance

RigCheck maintains a comprehensive automated test suite with 31 tests and zero linter warnings.

### Run Backend Tests
```bash
source .venv/bin/activate
pytest -v
```

**Test Coverage Highlights**:
- **Authentication & Security (`tests/test_auth.py`)**: Successful login, wrong secret rejection, 5-attempt rate limit lockout (429), session revocation on logout, and CORS preflight policies for Render and Cloudflare origins.
- **Endpoint Protection (`tests/test_analyze_endpoint.py`, `tests/test_health.py`)**: Unauthenticated 401 rejections, sanitization of telemetry when logged out.
- **Compatibility Engine (`tests/test_compatibility.py`)**: PSU wattage matching and shortfall, CPU socket matches and mismatches, form factor restrictions, budget evaluations in IDR.
- **Image Validation (`tests/test_image_validation.py`)**: Rejection of unsupported MIME types, empty payloads, files > 10MB, and negative prices.
- **Vision Parser & Uncertainty (`tests/test_ollama_parser.py`)**: JSON extraction from markdown code fences, malformed JSON recovery, and uncertainty preservation auditing.
- **Profile Persistence (`tests/test_profile.py`)**: Default profile generation, atomic disk saves, and corrupted JSON recovery.

### Run Frontend Lint & Build
```bash
cd frontend
npm run lint    # oxlint: 0 warnings, 0 errors
npm run build   # tsc -b && vite build
```

---

## Live Demonstration Checklist

Follow this checklist to demonstrate RigCheck for evaluators or judges:

- [ ] **1. Station Lock Verification**: Open the app in an incognito window or phone browser. Verify the "Hardware Station Locked" modal appears. Attempt to submit an invalid secret and verify the 401 rejection.
- [ ] **2. Authenticated Unlock**: Enter the correct `ACCESS_SECRET`. Verify the station unlocks and the telemetry status shows "Ollama: Ready".
- [ ] **3. PC Profile Review**: Navigate to the **My PC Profile** tab. Review the configured components (e.g. 750W PSU, AM5 socket, ATX chassis, 8,000,000 IDR budget). Update the PSU wattage and verify changes persist.
- [ ] **4. Camera / Image Scan**: Navigate to the **Scanner** tab. Capture or upload a photo of a GPU or CPU box label (e.g., RTX 4070 or RTX 4090).
- [ ] **5. Price & Analysis Execution**: Enter an observed price in IDR (e.g., Rp 11,500,000). Tap **Run RigCheck Analysis**.
- [ ] **6. Report Inspection**: Review the structured analysis report:
  - Extracted hardware specifications (brand, model, series, TDP, recommended PSU).
  - Vision extraction evidence (visible labels detected by Gemma 3 4B).
  - Compatibility check cards with clear **PASS**, **WARN**, or **FAIL** badges.
  - Budget evaluation vs. user profile.
- [ ] **7. Lock / Sign Out**: Tap the **Lock** button in the header. Verify the session is revoked and protected endpoints return to locked state.

---

## Recommended Screenshots for DEV Submission

1. **Mobile Station Locked Screen**: Demonstrates access control and security design on a phone viewport.
2. **Scanner View on Mobile Phone**: Displays the camera capture interface, file selection fallback, price input, and search toggle.
3. **Compatibility Report Card**: Shows a complete evaluation report with overall verdict, PSU check pass, and budget evaluation.
4. **Desktop Profile Canvas**: Displays the Warm Industrial Drafting interface showing CPU, Motherboard, GPU, PSU, and Budget settings.
5. **Terminal / Inference Telemetry**: Shows local Ollama vision execution (`gemma3:4b`) running on the host machine without external cloud dependencies.

---

## Privacy Boundaries & Known Limitations

### Privacy Boundaries
- **Zero Cloud AI**: Photos are never transmitted to Google, OpenAI, Anthropic, or any hosted vision service. All visual extraction is performed by Ollama on localhost.
- **Local Storage**: Your hardware configuration is stored strictly on your local PC disk (`data/user_profile.json`).
- **Temporary Uploads**: Uploaded images exist only in application RAM during model inference and are immediately freed.
- **Credential Safety**: SerpAPI keys and Access Secrets remain server-side on your host PC and are never compiled into client JavaScript bundles.

### Known Limitations & Future Work
- **Temporary Tunnel Lifespans**: Cloudflare Quick Tunnels generate a new random domain whenever restarted. For persistent remote access, a named Cloudflare Tunnel with an owned domain can be configured.
- **Physical Clearance Nuances**: Packaging labels rarely print exact physical card length in millimeters. While wattage and form factor are verified automatically, users should verify chassis clearance measurements against their case specifications.
- **Upcoming Features**: Memory generation validation (DDR4 vs DDR5) and BIOS revision checks for newer generation processors on older chipset motherboards.

---

## License

MIT License. Built for the Hacktoberfest DEV Challenge.
