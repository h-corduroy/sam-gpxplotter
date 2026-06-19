# Cursor 201 — Deep Dive Demo

**Audience:** Technical pilot group at Adobe, actively evaluating Cursor. They know the basics; they want advanced workflows.

**Repo:** `gpxplotter` — a Python library that reads GPX files and renders matplotlib plots + Folium maps, plus a FastAPI web app (`app/main.py`) that catalogs `.gpx` files and renders each as an interactive map.

**Why this repo works:** It's a library *and* a visual web app. That lets us show code-reasoning depth *and* browser automation in one story.

---

## Core principle: one story, not six feature demos

The prompt says **depth over breadth** and warns against "feature explanations." So we don't tour six features. We pick **one realistic feature request** and show how a power user ships it end-to-end. The advanced features appear *naturally* as the workflow demands them. That reads as "trusted advisor / power user" instead of "I read the changelog."

---

## The narrative spine (10–15 min live)

**The setup:** "A product manager filed a ticket — *Add an elevation-profile panel to each route map, plus a summary stat card (distance, elevation gain, max grade)._ Watch how I'd ship this in Cursor without babysitting it."

**The feature to build:** an **elevation profile + stats card** on the map page. It's visual (great for a live audience), touches the library *and* the web app, and is genuinely useful.

### How the features chain in

| Beat | Feature | What you show |
|---|---|---|
| 1. Kick off | **Skill** | We already have `run-gpx-catalog`. Show the agent boots the app from a codified skill — "this is how teams stop re-explaining setup to every new hire / every agent." |
| 2. Parallelize | **Multitasking + Subagents** | Fire one agent to add backend stat computation in the library, a second to build the frontend panel, while a **subagent explores** how `read_gpx_file` exposes elevation data. Narrate: "I'm not waiting on one thread." |
| 3. Verify visually | **Browser automation** | Agent runs the app, drives the browser to a route, screenshots the new elevation panel. The "aha": the agent *closes its own loop* — sees the result, not just writes code. |
| 4. Review | **Bugbot** | Run Bugbot on the diff live. The "always-on senior reviewer" tier — `resolve_gpx_path` / `sanitize_gpx_filename` handle untrusted uploads, a realistic place to flag path traversal. |
| 5. Offload | **Cloud agent** | Hand a follow-up ("write tests + docs for the new endpoint") to a cloud agent so it runs while you keep talking. Shows the local↔cloud handoff. |
| 6. Institutionalize | **Automation** | A scheduled automation that nightly validates every GPX file in the catalog still renders, or auto-triages new issues. The leadership point: "individual leverage → team leverage." |

**The thought-leadership message is the arc itself:**

> codify (skills) → parallelize (multitasking/subagents) → verify (browser) → guard (bugbot) → scale out (cloud) → institutionalize (automations)

---

## Concrete feature ideas per capability

### Skills (we have one; add a second to show range)
- A `gpx-feature-workflow` skill encoding *house style*: "when adding an endpoint, also add a test, update `index.html`, run Bugbot." The enterprise "aha" — skills encode *process*, not just commands.
- A `review-map-render` skill that boots the app + browser-screenshots a route, so any agent can self-verify UI work.

### Subagents
- `explore` subagent to map the data model (`gpxread.py` → what keys segments expose) before editing — parallel read-only exploration.
- Parallel implementer subagents: one on `gpxplotter/` (compute elevation gain/grade), one on `app/` (render panel).

### Multitasking
- Backend + frontend + docs in three concurrent background agents; you supervise. A strong visual of the agent list working at once.

### Cloud agents
- Offload "add pytest coverage for `/api/tracks` upload validation" to the cloud while the local demo continues.
- Bonus: kick one off *from Slack* (Slack MCP is available) for the "delegate from where you already work" moment.

### Bugbot
- Point it at the upload / path-resolution code. `sanitize_gpx_filename` / `resolve_gpx_path` handle untrusted uploads — a realistic place for Bugbot to flag traversal or content-type issues. Far more credible than a toy bug.

### Automations
- Nightly "render-health" automation: load every file in `gpx_files/`, assert each renders, open an issue if not.
- "New GPX uploaded → auto-generate a thumbnail + PR" style automation.

---

## Aha moments to land (this is what they're scoring)
1. **The agent verifies its own UI work in a browser** — most people don't know Cursor can do this.
2. **Skills = institutional memory.** The answer to "how do we make thousands of Adobe engineers use Cursor *consistently*?"
3. **Local + cloud + Slack are one continuum**, not separate products.
4. **Bugbot as a quality gate in the loop**, not an afterthought.

---

## Timeboxing (keep live demo ~12 min)
- **2 min** — framing + the ticket
- **6 min** — live build (skill boot → parallel agents → browser verify)
- **2 min** — Bugbot review
- **2 min** — hand-off to cloud agent + show the automation already running
- Keep pre-built fallbacks (recorded GIF / already-running cloud agent) in case live fails.

---

## Q&A / discussion prep
- **Models, context, memory:** be ready to discuss model/tool selection, context windows, and how skills/rules persist context across sessions.
- **Field Engineering POV:** how AI reshapes engineering teams — leverage moves from "writing code" to "designing and supervising workflows."
