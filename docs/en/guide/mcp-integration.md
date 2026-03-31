# MCP Integration Guide

cc-company works with MCP (Model Context Protocol) servers. Setting up MCP servers allows the secretary to directly operate external services.

## How It Works

No special configuration is needed on the cc-company side. Just add MCP servers to Claude Code, and the secretary will automatically use them.

```
You: Schedule a meeting with Company A tomorrow at 2pm

Secretary: Added to your calendar!
           I've also added "Prepare meeting materials for Company A" to your TODOs.
```

## Recommended MCP Servers

### Notion (Official)

Connect with your knowledge base and databases. The secretary can read and update Notion pages.

**Method 1: OAuth (Recommended)**

```bash
claude mcp add-json notion '{"type":"http","url":"https://mcp.notion.com/mcp"}'
```

After running, OAuth authentication opens in your browser. No manual API key setup needed.

**Method 2: API Token**

```bash
claude mcp add notion -e NOTION_TOKEN=ntn_YOUR_TOKEN -- npx -y @notionhq/notion-mcp-server
```

Create an API token at [Notion Integrations](https://www.notion.so/my-integrations).

**Capabilities:**
- Read, create, and update Notion pages
- Search and update databases
- Secretary can reference your existing knowledge base

---

### Google Calendar

Schedule management. The secretary can register meetings and set reminders.

```bash
claude mcp add google-calendar \
  -e GOOGLE_OAUTH_CREDENTIALS=/path/to/gcp-oauth.keys.json \
  -- npx -y @cocal/google-calendar-mcp
```

**Prerequisites:**
1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Calendar API
3. Create OAuth 2.0 credentials (Desktop app type)
4. Download the credentials JSON

**Capabilities:**
- Create, view, modify, and delete events
- Show today's/this week's schedule
- Check availability
- Manage recurring events

---

### GitHub (Official)

Repository management. Great synergy with the Engineering department.

**Method 1: HTTP (Recommended)**

```bash
claude mcp add-json github '{"type":"http","url":"https://api.githubcopilot.com/mcp","headers":{"Authorization":"Bearer YOUR_GITHUB_PAT"}}'
```

**Method 2: Docker**

```bash
claude mcp add github \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=YOUR_PAT \
  -- docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server
```

Create a token at [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens).

**Capabilities:**
- Create, view, and search issues
- Manage and review PRs
- Check repository status
- Code search

---

### Slack (Official)

Team communication. Works well with Sales and PM departments.

**Method 1: OAuth (Recommended)**

```bash
claude mcp add-json slack '{"type":"http","url":"https://mcp.slack.com/mcp","oauth":{"clientId":"1601185624273.8899143856786","callbackPort":3118}}'
```

After running, Slack OAuth authentication opens in your browser.

**Method 2: Install as plugin**

```bash
claude plugin install slack
```

**Capabilities:**
- Send and check messages
- Monitor channel activity
- Look up user info
- Client communication reminders

::: warning Note
Your workspace admin must have approved MCP integration.
:::

---

## Setup Methods

### Via Command (Recommended)

Just run the `claude mcp add` commands above. Restart Claude Code after setup.

### Manual Configuration

**Global settings (all projects):** `~/.claude/settings.json`

```json
{
  "mcpServers": {
    "notion": {
      "type": "http",
      "url": "https://mcp.notion.com/mcp"
    }
  }
}
```

**Project settings (specific project only):** `.claude/settings.json`

::: tip
Put frequently used services (calendar, Notion) in global settings, and project-specific ones (GitHub) in project settings.
:::

---

## Examples with the Secretary

Once MCP servers are set up, the secretary uses them naturally.

```
> What's my schedule this week?
Secretary: Let me check your calendar.
      - Monday 10:00 Weekly meeting with Company A
      - Wednesday 14:00 Hearing with Company B
      - Friday All day Tax filing deadline
      Is the proposal for Company B on Wednesday ready?

> Summarize the meeting notes with Company A in Notion
Secretary: Done. Created a meeting notes page in Notion.
           I've also saved a summary in secretary/notes/.

> Create an issue for this bug
Secretary: Created an issue on GitHub.
           I've also logged it in engineering/debug-log/.
```

## Works Without MCP Too

cc-company works perfectly fine without any MCP servers. The secretary functions fully with just file management within `.company/`.

MCP is a "nice to have" option.
