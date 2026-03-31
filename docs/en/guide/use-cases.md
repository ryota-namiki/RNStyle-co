# Use Cases

cc-company grows differently depending on who uses it. Here are 3 concrete scenarios.

## 1. Freelance Web Developer

**Profile:** Primarily contract development. Juggling multiple clients simultaneously.

### Setup

```
Secretary: First, tell me about your business or activities.
You: Freelance web development. Mostly contract work.

Secretary: What are your current goals or challenges?
You: Clients are piling up and I can't keep up with task management. Worried about missing invoices.
```

### Month 1: Running with just the secretary

```
> What should I do today?
Secretary: Here are today's TODOs:
  - [ ] Client A: Review top page feedback | Priority: High
  - [ ] Client B: Create estimate
  - [ ] Organize tax receipts

> Got a revision request from Client A on Slack
Secretary: Added to TODOs!
  - [ ] Client A: Handle Slack revision request | Priority: High
```

### Month 2: Sales & Finance departments added

```
Secretary: Client-related tasks are increasing.
           Shall I create a Sales department? It can organize client info and deals.
You: Sure, create it

Secretary: Invoice management has come up several times too.
           Shall I create a Finance department?
You: That too
```

### Final Organization

```
.company/
├── secretary/    ← Daily TODOs & notes
├── sales/        ← Client info & deal management
│   ├── clients/
│   │   ├── company-a.md
│   │   └── company-b.md
│   └── proposals/
└── finance/      ← Invoices & expenses
    ├── invoices/
    └── expenses/
```

---

## 2. Solo Developer (SaaS Launch)

**Profile:** Full-time employee. Building a SaaS on the side. Pre-launch.

### Setup

```
Secretary: First, tell me about your business or activities.
You: I'm building a side project — a task management SaaS.

Secretary: What are your current goals or challenges?
You: I want to launch within 3 months. Too many things to do and can't prioritize.
```

### Month 1: Organizing ideas with the secretary

```
> Should I use Supabase Auth or Clerk for authentication?
Secretary: Let's brainstorm! Here are the characteristics of each...
           ...
           Conclusion: Start simple with Supabase Auth. Can migrate to Clerk later if needed.
           I'll save this to notes.

> Oh, I wanted to add a FAQ to the pricing page
Secretary: Captured in inbox!
```

### Month 2: PM & Engineering departments added

```
Secretary: Development task notes are piling up.
           Shall I create a PM department for milestones and tickets?
You: Please do

Secretary: Technical design notes are accumulating too.
           Shall I organize them in an Engineering department?
You: That sounds good
```

### Month 3: Marketing added for launch prep

```
> I need to start preparing the LP and announcements
Secretary: Shall I create a Marketing department?
           It can manage LP, social media announcements, and blog posts.
You: Create it!
```

### Final Organization

```
.company/
├── secretary/      ← Ideas & daily notes
├── pm/             ← Launch milestones
│   ├── projects/
│   │   └── saas-launch.md
│   └── tickets/
├── engineering/    ← Technical design & debug logs
│   ├── docs/
│   │   ├── auth-design.md
│   │   └── db-schema.md
│   └── debug-log/
└── marketing/      ← LP & announcement plans
    ├── content-plan/
    │   ├── landing-page.md
    │   └── launch-blog-post.md
    └── campaigns/
        └── launch-campaign.md
```

---

## 3. Video Creator

**Profile:** Primarily active on YouTube. Also takes corporate projects.

### Setup

```
Secretary: First, tell me about your business or activities.
You: I make YouTube videos. Also do corporate projects.

Secretary: What are your current goals or challenges?
You: My posting schedule is inconsistent. Running out of content ideas too.
```

### Month 1: Managing ideas with the secretary

```
> I got a video idea. "Premiere Pro tutorial for beginners"
Secretary: Nice! I'll save it to inbox.

> What should I post next week?
Secretary: Let's look at your stocked ideas:
  - Premiere Pro tutorial for beginners
  - 5 Vlog editing techniques
  - After Effects vs Motion Graphics comparison
  Which one?
```

### Month 2: Marketing department added

```
Secretary: Content planning consultations are increasing.
           Shall I create a Marketing department to manage your posting schedule?
You: Yes, I've been wanting that!
```

### Month 3: Sales department added (corporate projects growing)

```
> Got an inquiry from Company D about a project
Secretary: Great! Corporate project management is growing too.
           Shall I create a Sales department for proposals and client management?
You: Create it
```

### Final Organization

```
.company/
├── secretary/      ← Idea notes & daily memos
│   ├── inbox/      ← Stock content ideas
│   ├── todos/      ← Filming & editing TODOs
│   └── notes/      ← Brainstorming notes
├── marketing/      ← Posting schedule & content planning
│   ├── content-plan/
│   │   ├── premiere-pro-tutorial.md
│   │   └── vlog-editing-tips.md
│   └── campaigns/
└── sales/          ← Corporate project management
    ├── clients/
    │   └── company-d.md
    └── proposals/
```

---

## Common Patterns

What's consistent across all cases:

1. **Start with just the secretary** — Easy to get going
2. **Departments grow through usage** — No need to decide everything upfront
3. **Every organization is different** — Same plugin, different growth paths
4. **Just talk to the secretary** — No need to be aware of departments
