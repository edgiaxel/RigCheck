*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 1: Touch Grass](https://dev.to/challenges/hacktoberfest-week1-2026-10-05)*

## What I Built

**RigCheck** is a privacy-first PC component compatibility assistant that helps hardware shoppers make confident decisions in physical computer stores, electronic flea markets, and secondhand swaps—away from desktop desks and without handing hardware photos over to hosted cloud AI platforms.

### The Real-World "Touch Grass" Problem
When you are physically browsing computer parts in a store or buying a used graphics card from a local seller, you need immediate answers to critical hardware questions:
- *Will this graphics card fit within my home power supply's wattage ceiling?*
- *Does this CPU match my existing motherboard's socket?*
- *Is this motherboard form factor compatible with my case?*
- *Does this asking price fit within my planned upgrade budget in IDR?*

Existing tools require tedious manual entry on desktop setups (e.g., PCPartPicker) or require uploading photos of physical boxes and serial numbers to external proprietary AI clouds. 

RigCheck changes this workflow:
1. You take a photo of a component label or retail box using your phone camera.
2. Your phone connects to your home PC over HTTPS via a secure Cloudflare Tunnel.
3. Your own PC runs **Gemma 3 4B** vision inference locally through **Ollama**.
4. The extraction pipeline evaluates verified physical/electrical specs against your home PC profile stored on your own disk.
5. You receive an unambiguous compatibility verdict (**Pass**, **Warning**, or **Fail**) directly on your phone within seconds.
6. The uploaded image is processed in RAM and discarded immediately. No images or hardware profiles are sent to external cloud AI providers.

---

## Demo

- **Deployed Static Frontend (Render)**: [https://rigcheck.onrender.com](https://rigcheck.onrender.com) *(or your deployed Render static URL)*
- **Local Backend & Tunnel Pipeline**: Connects on-demand to your local PC running FastAPI + Ollama via Cloudflare Tunnel.

### Visual Workflow
1. **Camera Scanner**: Mobile browser opens your device camera (`capture="environment"`) to snap a photo of any CPU, GPU, or motherboard box label.
2. **PC Bridge**: The client sends the image payload directly to your local PC via the configured Cloudflare Tunnel URL.
3. **Structured Verdict**: The response breaks down:
   - **PSU Wattage Capacity**: Evaluates GPU TDP and recommended wattage against your installed PSU.
   - **Socket Match**: Checks CPU socket (AM4, AM5, LGA1700, LGA1851) against your motherboard socket.
   - **Form Factor Clearance**: Checks ATX, Micro-ATX, and Mini-ITX chassis constraints.
   - **Budget Evaluation**: Compares observed street price in Indonesian Rupiah (IDR) against your configured budget ceiling.

---

## Code

The complete source code is open source on GitHub:

{% github edgiaxel/RigCheck %}

Repository: [https://github.com/edgiaxel/RigCheck](https://github.com/edgiaxel/RigCheck)

### Project Architecture
```text
[Mobile Phone in Store]
       │
       ▼  (HTTPS / Mobile Camera Upload)
[Render Static Site: frontend/dist]
       │
       ▼  (Cross-Origin API Bridge)
[Cloudflare Quick Tunnel: https://<id>.trycloudflare.com]
       │
       ▼  (Bound to 127.0.0.1:8000)
┌─────────────────────────────────────────────────────────────┐
│ FastAPI Local Backend (Host PC)                             │
│  ├── CORS Middleware (Cross-Origin Render Support)          │
│  ├── Streaming In-Memory Image Validator                    │
│  ├── Ollama Client (Local Vision Prompting)                 │
│  ├── Rule Evaluation Engine (Deterministic Checks)          │
│  └── Local Profile Storage (data/user_profile.json)         │
└──────────────────────────────┬──────────────────────────────┘
                               │
       ┌───────────────────────┴───────────────────────┐
       ▼ (Private Localhost 11434)                     ▼ (Host PC Storage)
┌──────────────────────────────────────┐        ┌──────────────────────┐
│ Ollama Service: gemma3:4b (Vision)   │        │ User PC Profile      │
│ 100% On-Device Visual Extraction     │        │ Private JSON Storage │
└──────────────────────────────────────┘        └──────────────────────┘
```

---

## How I Built It

### 1. Local Open-Weight Vision Model: Google Gemma 3 4B on Ollama
Instead of relying on hosted cloud vision APIs, RigCheck uses Google's open-weight **Gemma 3 4B** (`gemma3:4b`) running on a local Ollama instance.

- **Structured Extraction**: The model is prompted with a strict JSON contract to extract:
  - `brand`, `model`, `series_or_chipset`, `category`
  - `power_tdp_watts`, `recommended_psu_watts`
  - `socket`, `form_factor`
  - `visible_labels`, `confidence_notes`
- **Uncertainty Preservation**: If a parameter (such as exact clearance or TDP) is missing or illegible from the retail box, Gemma 3 returns `null` and explicitly logs it in `unresolved_fields`. RigCheck's evaluation engine flags this as `UNKNOWN` rather than inventing hardware specifications.

### 2. Optional Technical Reference Search (SerpAPI)
When a hardware model is confirmed by visual packaging (e.g., `MSI GeForce RTX 4070 Gaming X Trio`) but the packaging omits specific power numbers, RigCheck can optionally query technical reference sources using SerpAPI.
- **Privacy Boundary**: Only technical hardware identifiers are queried. Raw photos, location data, and user hardware configurations never leave the local PC.

### 3. FastAPI Deterministic Engine & In-Memory Pipeline
- **Zero Image Persistence**: Images are read in chunks up to 10MB directly into RAM, converted into base64 for Ollama's local vision endpoint, and never written to disk.
- **Rule Engine**: Evaluates mathematical limits (PSU headroom = installed wattage - component wattage) and categorical constraints (socket and form factor matching).

### 4. Responsive React 19 + TypeScript Frontend
- Built with Vite, TypeScript, and React 19.
- Custom **Warm Industrial Drafting** design aesthetic without bulky UI frameworks.
- Dual mobile/desktop layouts: full PC profile configuration on desktop, direct camera capture and verdict cards on phone viewports.
- Configurable cross-origin API client that supports direct same-origin serving as well as Render static deployment connected to Cloudflare Quick Tunnels.

---

## Why Does Open Innovation Matter?

Open innovation—exemplified by open-weight models like **Gemma 3** and local runtimes like **Ollama**—fundamentally redefines what personal computing assistants can be:

1. **True Privacy for Real-World Workflows**:  
   Capturing photos of physical hardware, room interiors, and product labels should not require streaming personal imagery to third-party corporate data centers. Open-weight models make high-performance computer vision run directly on your existing home graphics card.
2. **Deterministic Trust over Hallucinations**:  
   Closed commercial APIs often prioritize conversational answers that disguise uncertainty. Open models allow custom system prompting, strict schema validation, and complete control over how uncertainty is audited.
3. **No Per-Scan API Tolls**:  
   Hardware shoppers shouldn't have to worry about running out of paid tokens while testing multiple parts at a swap meet. Once installed on your PC, local inference is free, private, and unlimited.

---

## My Agent Session

This entire application—from the FastAPI backend architecture, local Ollama vision pipeline, responsive React drafting UI, to the Cloudflare tunnel setup and Render deployment—was pair-programmed in **Antigravity IDE** with **Greg** (agent).

<!-- You can link or embed your DevRelay session transcript here: -->
<!-- {% agent_session <session_id> %} -->

---

## Prize Categories

- **Open-Source AI Challenge Week 1: Touch Grass**
- **Best Use of Open-Weight Models (Google Gemma 3 4B)**
