# File Structure

## Plugin Structure

```
RNstyle co./
├── .claude-plugin/
│   └── marketplace.json        ← Marketplace registration info
├── .github/
│   └── workflows/
│       └── deploy-docs.yml     ← Auto-deploy documentation
├── plugins/
│   └── company/
│       ├── .claude-plugin/
│       │   └── plugin.json     ← Plugin metadata
│       └── skills/
│           └── company/
│               ├── SKILL.md    ← Skill definition (entire workflow)
│               └── references/
│                   ├── departments.md         ← Department templates
│                   └── claude-md-template.md  ← CLAUDE.md generation template
├── docs/                       ← This documentation (VitePress)
├── package.json
├── README.md
└── LICENSE
```

## Generated Organization Structure

The `.company/` folder created after running `/company`.

### Initial State

```
.company/
├── CLAUDE.md              ← Organization rules & owner info
└── secretary/
    ├── CLAUDE.md           ← Secretary behavior rules
    ├── inbox/              ← Quick capture
    ├── todos/              ← Daily task management
    │   └── YYYY-MM-DD.md
    └── notes/              ← Brainstorming & consultation notes
```

### After Adding Departments

```
.company/
├── CLAUDE.md
├── secretary/
│   ├── CLAUDE.md
│   ├── inbox/
│   ├── todos/
│   └── notes/
├── research/              ← Added department
│   ├── CLAUDE.md
│   └── topics/
└── pm/                    ← Added department
    ├── CLAUDE.md
    ├── projects/
    └── tickets/
```

## File Naming Rules

| Pattern | Format | Example |
|---------|--------|---------|
| Daily files | `YYYY-MM-DD.md` | `2026-03-19.md` |
| Topic files | `kebab-case.md` | `competitor-analysis.md` |
| Decision logs | `YYYY-MM-DD-decisions.md` | `2026-03-19-decisions.md` |
| Templates | `_template.md` | `_template.md` |

## TODO Format

```markdown
- [ ] Task description | Priority: High/Normal/Low | Due: YYYY-MM-DD
- [x] Completed task | Done: YYYY-MM-DD
```

## Operational Rules

- **One file per day**: If a file for the same date exists, append to it
- **Date check**: Always verify today's date before file operations
- **No overwriting**: Existing files are append-only
- **When in doubt, inbox**: If unsure where to categorize, put it in `secretary/inbox/`
