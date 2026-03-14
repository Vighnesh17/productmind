# ProductMind AI

An enterprise SaaS where companies get their own AI Product Manager agent. The agent connects to their tools (Jira, Slack, Notion, GitHub, analytics) and handles the operational side of product management — status updates, sprint planning, backlog grooming, feedback synthesis, stakeholder communication — so human PMs can focus on strategy and vision.

The real enemy is the **coordination tax**: the 30–50% of a PM's week spent manually pulling status from 3 tools, writing updates that could be automated, and chasing context that already exists somewhere. ProductMind kills the coordination tax.

## Current Phase
Phase 1: Walking Skeleton

---

## Key Principles

- **The agent is a PM, not a chatbot.** It acts proactively, has a point of view, pushes back on bad decisions, and reasons across all connected tools simultaneously. See "PM vs Chatbot" section below for the exact behavioral criteria.
- **Trust is earned progressively, per workflow.** Autonomy is granted at the workflow level, not globally. A PM can fully automate sprint Slack updates while keeping stakeholder emails in draft-only mode. See Workflow Autonomy Model below.
- **Cross-tool intelligence is the moat.** The value is catching the gap between what tools say and what's actually true — not summarising data from one tool.
- **Every action is logged with reasoning.** Every output cites its sources. Every conclusion shows its work. Enterprises need this to trust AI.
- **WATCH mode must be outrageously valuable.** The most conservative mode must be worth paying for on its own. Do not design features that only matter in ACT mode.
- **MVP integrations: Jira, Slack, Notion.** Don't build more until these three work perfectly. "Perfectly" has a definition — see Integration Quality Gates below.

---

## Who We're Building For

### The User (uses it daily)
**Individual PM / APM at a 20–500 person tech company.**
- Spends 30–50% of their week on coordination: writing sprint updates, chasing ticket status, compiling stakeholder comms
- Fears: AI making them look bad in front of their manager or stakeholders
- Wants: to walk into Monday standup already knowing everything, to never be caught off-guard, to spend their time on actual product strategy
- Success signal: "I reviewed the agent's sprint report and it was more accurate than what I'd have written in 30 minutes"

### The Buyer (approves the budget)
**VP Product / Head of Product / CTO at the same company.**
- Cares about: team efficiency, better visibility into what PMs and teams are actually doing, not growing headcount to handle coordination
- Fears: AI causing a stakeholder embarrassment (wrong data sent to the CEO)
- Success signal: "My PMs spend less time on status and more time on strategy, and I have better visibility without scheduling more meetings"
- Budget: $300–2000/month per team

### The Influencer (ally or blocker)
**Engineering Manager / Scrum Master.**
- Ally when: agent reduces their coordination burden too (fewer "what's the status of X?" Slack pings)
- Blocker when: agent feels like surveillance or encroaches on their process ownership
- Design for: agent surfaces insights to the PM, not the EM — PMs decide what to share upward

---

## PM vs Chatbot — Behavioral Criteria

This is the north star for every feature decision. When in doubt, ask: "is this PM behavior or chatbot behavior?"

| Chatbot | PM Agent |
|---|---|
| Responds to queries | Acts proactively — surfaces issues before asked |
| Summarises what it finds | Has a point of view ("this sprint is at risk because...") |
| Produces generic output | Output is org-specific — uses the team's terminology, references their history |
| Forgets after the session | Remembers. Builds context over months. |
| Executes instructions | Pushes back ("that's overcommitting the team by 40% based on your last 6 sprints") |
| Reasons about one tool at a time | Reasons across all connected tools simultaneously |
| No audit trail | Every conclusion has a citation with source and timestamp |

**The test for every new feature:** Would a sceptical PM read the output and say "I couldn't have written that better in 15 minutes"? If yes: PM behaviour. If no: chatbot behaviour. Do not ship chatbot behaviour.

---

## Workflow Autonomy Model

Trust is not a global property of the agent — it's a per-workflow configuration. A PM might fully automate sprint Slack updates on day one while keeping PRD drafts in review-only mode indefinitely. That's correct behaviour, not a limitation.

### The Three Modes

```
WATCH  → Agent observes and surfaces insights. PM reads output and acts themselves.
         · No drafts created. No artifacts saved.
         · Use when: PM wants signal but not suggestions yet.
         · Default for: new workflows, sensitive action types (Jira mutations, external sends).

DRAFT  → Agent creates the artifact. Nothing leaves the agent without PM approval.
         · PM gets one-click approve / edit / reject on every output.
         · Use when: PM trusts the agent's judgment but wants a final eye.
         · Default for: most workflows on day one.

ACT    → Agent executes autonomously within defined rules. Logs everything.
         · Every action appears in the audit log with full reasoning.
         · PM can undo any ACT-mode action from the log.
         · Use when: PM has seen consistent accuracy and wants full automation.
         · Examples: auto-post sprint update to Slack, auto-create standup summary.
```

### Applied Per Workflow

```
WORKFLOW                    | DEFAULT MODE | NOTES
────────────────────────────────────────────────────────────────────────
Sprint Status Report        | DRAFT        | PM reviews before it goes anywhere
Standup Slack Summary       | DRAFT        | Move to ACT once accuracy is proven
Stakeholder Weekly Update   | DRAFT        | Likely stays DRAFT — high stakes
Ticket Status Correction    | WATCH        | Agent flags, PM decides whether to update
PRD Draft                   | WATCH        | PM wants suggestions, not a generated doc
Sprint Planning             | DRAFT        | PM approves the plan before committing
Blocker Escalation          | DRAFT        | PM approves before pinging EM
────────────────────────────────────────────────────────────────────────
```

### Admin Controls

```
· MAX MODE CAP per action category:
  e.g. "Jira ticket mutations: max DRAFT (company policy)"
  e.g. "Slack posts: max ACT"
  Admins set the ceiling. PMs configure within it.

· GLOBAL PAUSE TOGGLE:
  One click sets ALL workflows to WATCH instantly.
  Reversible. Logged with timestamp and who triggered it.
  Use when something goes wrong — no need to reconfigure each workflow.

· AUDIT LOG:
  Every DRAFT shown to PM, and every ACT-mode action, is logged:
  what was done, why (agent's reasoning), what sources were used, timestamp.
  ACT-mode actions show an undo button for 24 hours.
```

### Earning More Autonomy

The system surfaces readiness signals — it never auto-promotes. The PM decides.

> "Your Sprint Status Reports have been approved without edits 12 times in a row. Want to switch this workflow to ACT mode?"

This is earned trust made visible. The PM acts on it when they're ready, not when a timer says so.

```
MODE TRANSITIONS (per workflow):

  WATCH ──────────────────► DRAFT ──────────────────► ACT
    │     PM enables DRAFT    │     PM enables ACT     │
    │                         │                        │
    ◄─────────────────────────◄────────────────────────┘
         PM revokes or admin       PM revokes or admin
         cap prevents it           cap prevents it

  GLOBAL PAUSE:
  Any mode ──────────────────────────────────────► WATCH (all workflows)
                  Admin hits pause                  Instant, reversible
```

**Design rule:** WATCH mode must be outrageously valuable on its own. DRAFT mode is where most customers will live. ACT mode is the reward for teams that lean in. Never design a feature that only matters in ACT mode.

---

## Onboarding — How the Agent Learns a New Team

Cold start is the hardest problem. On Day 1 the agent knows nothing about the team. Getting to "genuinely useful" requires a deliberate onboarding arc.

### Week 1 — Listen and Learn
- Agent reads: last 3 months of Jira history, last 30 days of Slack (specified channels), Notion workspace index
- Agent builds a "Team Profile" internally:
  - Average sprint velocity (points and tickets)
  - Typical cycle time per ticket type
  - Common blockers and their patterns
  - Team vocabulary (what they call things)
  - Who works on what
  - How "done" is actually used vs. how Jira defines it

- Agent shows the PM a **Team Profile Summary** at end of Week 1:
  > "Here's what I learned about your team. Your average sprint velocity is 24 points. Your most common blocker is external dependencies (appears in 40% of delayed tickets). Your team calls the design review step 'UX sign-off' not 'Design Review'. Does this look right?"

- PM reviews, corrects anything wrong. These corrections are the most important training data.

### Week 2 — Make Predictions, Show Work
- Agent makes predictions ("I think PROJ-123 will miss the sprint") and shows its reasoning
- PM rates accuracy at end of sprint
- Agent learns from discrepancies explicitly ("I predicted X but it was Y — I'll adjust my model for external dependencies")
- All workflows remain in WATCH or DRAFT mode. No autonomous actions.

### Week 3+ — Earn Trust
- PM has seen enough outputs to calibrate trust per workflow
- PM decides when to move each workflow to DRAFT or ACT (not the system)
- Agent continues to show its reasoning on every output
- Accuracy rate per workflow is tracked and visible in the PM's dashboard
- System surfaces readiness signals: "This workflow has been approved without edits 10 times. Ready to automate?"

**Design rule:** The onboarding arc is a product feature, not an implementation detail. It must be designed before the first prompt is written.

---

## When the Agent is Wrong

This will happen frequently in the first month. The wrong-rate handling is what determines whether trust builds or collapses.

### The Correction Flow
1. Every agent output has a **"Flag as inaccurate"** option (not buried — one click)
2. PM selects what's wrong: "Wrong ticket status" / "Missing context" / "Wrong interpretation" / "Outdated info" / "Other"
3. Agent responds: "Got it — I marked PROJ-123 as still In Progress based on the last comment, but I can see it was actually Done as of Thursday. I'll use commit activity as a signal next time, not just comments."
4. Correction is logged. Wrong-rate is tracked.

### Wrong-Rate Dashboard (admin view)
- Accuracy rate this week / last 4 weeks (trending up or down)
- Most common error type
- Which integration causes most errors (usually Jira — data hygiene)

### Design rule
The agent must never be defensive when corrected. It must acknowledge, explain its original reasoning, and state what it will do differently. This is the trust-building loop.

---

## The Data Hygiene Problem

Real teams have terrible Jira hygiene. Tickets stay "In Progress" for 3 weeks. Notion pages are stale. The Slack decision was never written down in Jira. The agent inherits this mess.

**The agent is a data quality driver, not a data quality victim.**

When the agent detects a likely stale or inconsistent record, it surfaces it:
> "PROJ-123 has been 'In Progress' for 9 days with no Jira updates, but Tom mentioned in #backend on Thursday that it's actually done. Want me to flag this for you to update, or shall I draft the update for your review?"

This turns a liability into a feature. Over time, teams with ProductMind have better Jira hygiene — not because the agent forced it, but because it makes the cost of bad hygiene visible and the fix frictionless.

**Confidence signals the agent uses:**
- Time since last Jira update (staleness indicator)
- Slack activity in relevant channels vs. Jira status
- Commit/PR activity (via GitHub when connected) vs. ticket status
- Comment content — does it contradict the ticket status?

**Agent must always be transparent about confidence:**
> "Sprint status confidence: 70%. Four tickets haven't been updated in 5+ days — my status for those is based on Slack activity, not Jira."

---

## Workflow Variation — Adapting to Each Team

Every team works differently. The agent must adapt to the team, not impose a workflow.

**What the agent learns in onboarding:**
- Sprint cadence (1 week, 2 week, custom?)
- Ticket types and what they mean to this team
- Their definition of "done" in practice
- Which Slack channels matter for product (not all of them)
- How they use Notion (PRDs? meeting notes? roadmaps? all of the above?)
- Their stakeholder communication style (brief Slack updates vs. detailed Notion pages)

**What the agent never assumes:**
- That "In Progress" means the same thing across teams
- That the PM wants the output in a specific format without being told
- That every sprint has the same goals structure
- That GitHub/analytics are connected (treat each integration as optional)

**Configuration the PM controls:**
- Which Slack channels the agent monitors
- The output format for recurring reports (can edit the template)
- What "blocked" means for their team (custom definition)
- Notification preferences

---

## Integration Quality Gates

Before expanding beyond Jira + Slack + Notion, each integration must clear these bars:

**Jira works perfectly when:**
- Agent describes sprint status with >85% factual accuracy vs. PM's own review
- Agent catches "Jira says X but reality is Y" discrepancies before the PM does
- Agent can draft a sprint plan based on historical velocity that PM finds realistic
- Agent identifies and names blockers before the PM asks

**Slack works perfectly when:**
- Agent surfaces decisions buried in threads (not just discussions)
- Agent correctly identifies what was *decided* vs. what was *discussed*
- Agent can answer "what did the team decide about X last week?" with correct citation
- Signal-to-noise ratio is high — agent doesn't surface irrelevant messages

**Notion works perfectly when:**
- Agent understands the relationship between PRDs and Jira tickets
- Agent notices when a PRD decision contradicts current Jira ticket scope
- Agent drafts Notion pages that match the team's existing style and structure
- Agent doesn't create orphaned pages

**Cross-tool works perfectly when:**
- Sprint status report cites all three sources correctly
- Agent proactively surfaces one cross-tool inconsistency per sprint without being asked
- PM finds the cross-tool insight the most valuable part of the output

---

## Phase 1 Walking Skeleton — Exact Scope

**Definition of done for Phase 1:**
> A PM can connect their Jira account, ask the agent "what's my sprint status and what should I be worried about?", and receive a response that is more accurate and more useful than what they'd have written themselves in 30 minutes — with full citations — in under 2 minutes.

**In scope:**
- Single tenant (one team)
- Sprint Status Report workflow in **DRAFT mode** (PM reads before anything goes anywhere)
- Jira integration: read sprint, tickets, history
- Slack integration: read specified channels
- Audit log: every output shows sources + reasoning
- Correction flow: PM can flag wrong outputs
- Team Profile: agent shows what it learned after onboarding read

**Out of scope for Phase 1:**
- Notion integration (Phase 2)
- ACT mode for any workflow (Phase 2 when accuracy is proven)
- Multi-tenant
- Backlog grooming, stakeholder comms, sprint planning workflows
- Admin mode-cap controls (Phase 2)

**Sprint Status Report — output spec:**
```
Sprint: [Name] · Day [X] of [Y] · [N] tickets open

Status: ON TRACK / AT RISK / OFF TRACK

Highlights:
· [What's going well — specific tickets or patterns]

Risks:
· [Risk 1] — [why it's a risk, cited from Jira/Slack]
· [Risk 2] — ...

Blockers requiring PM action:
· [Blocker] — [who is blocked, since when, suggested action]

Confidence: [%] — [note if any data is stale or inferred from Slack rather than Jira]

Sources: Jira sprint [name] (synced [time]), #[channel] (last read [time])
```

**Phase 1 success criteria:**
- PM reviews one full sprint cycle using the agent
- Factual accuracy of sprint reports > 80%
- PM says they would pay for this
- Wrong-rate is tracked (even if high — we need the data)

---

## Phase Roadmap

**Phase 1 — Walking Skeleton (now)**
Jira + Slack read-only. Sprint Status Report in DRAFT mode. Single tenant. Manual onboarding. Zero autonomous actions — PM reads every output.

**Phase 2 — Value Proof**
Add Notion. Add workflows: backlog grooming, stakeholder update draft, sprint planning. Introduce ACT mode for proven low-stakes workflows (Slack standup summaries). Multi-tenant (3–5 beta customers). Agent-assisted onboarding. Accuracy tracking per workflow. Admin mode-cap controls. Admin dashboard.

**Phase 3 — Moat Building**
Add GitHub (link PRs to tickets to Slack decisions). ACT mode for more workflow types as accuracy compounds. Agent has opinions — proactively surfaces risks before sprint start. Agent knows PM preferences and stakeholder styles. Cross-tenant benchmarks (anonymised). SOC2 Type II.

---

## Decisions Log
(Claude Code: update this as you make architecture decisions)

---

## gstack
use the /browse skill from gstack for all web browsing, never use mcp__claude-in-chrome__* tools, and lists the available skills: /plan-ceo-review, /plan-eng-review, /review, /ship, /browse, /qa, /setup-browser-cookies, /retro.
