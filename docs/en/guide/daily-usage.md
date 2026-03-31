# Daily Usage with Secretary

After setup, just talk to your secretary with `/company`.

## TODO Management

```
> /company
Secretary: Good morning! What can I help you with?

> What should I do today?
Secretary: Here are today's TODOs:
  - [ ] Send estimate to Client A
  - [ ] Review LP design doc

> Add "Implement Stripe payments", high priority
Secretary: Added!
  - [ ] Implement Stripe payments | Priority: High
```

TODOs are saved in `secretary/todos/YYYY-MM-DD.md`.

## Brainstorming & Consultation

```
> I want to brainstorm about pricing models
Secretary: Sure! Tell me what you're thinking.
           Do you have any options in mind?

> I'm torn between subscription and one-time purchase
Secretary: Let's organize the pros and cons of each...
           ...
           Shall I save the conclusion to notes?
```

Results are saved in `secretary/notes/`.

## Quick Notes

```
> Oh, I just thought of something — I should add a FAQ section to the LP
Secretary: Noted!
  → Recorded in secretary/inbox/2026-03-19.md
```

Ideas and quick thoughts are captured in `secretary/inbox/`.

## Dashboard

```
> Dashboard
Secretary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Company Dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Secretary's Office:
  TODOs (today): 3 incomplete / 1 complete
  Inbox: 2 unprocessed

Anything else?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Auto-Recording

The secretary automatically records the following without being asked:

| Content | Saved to |
|---------|----------|
| Decisions | `secretary/notes/YYYY-MM-DD-decisions.md` |
| Learnings | `secretary/notes/YYYY-MM-DD-learnings.md` |
| Ideas | `secretary/inbox/YYYY-MM-DD.md` |
