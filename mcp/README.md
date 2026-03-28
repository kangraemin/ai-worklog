# worklog-mcp

**The project doc that writes itself.**

MCP server that manages worklogs and keeps `PROJECT.md` up to date — across Claude Code, Cursor, and Claude Desktop.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![MCP](https://img.shields.io/badge/MCP-compatible-blue)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://python.org)

---

## What It Does

- **Worklog** — records what you worked on into `.worklogs/YYYY-MM-DD.md`, optionally syncs to Notion
- **Project doc** — creates and maintains `PROJECT.md` with structure, decisions, and solved problems
- **Gap detection** — compares recent git commits to `PROJECT.md` and surfaces what's missing
- **Any client** — Claude Code, Cursor, Claude Desktop, anything MCP-compatible

## Install

```bash
git clone https://github.com/kangraemin/worklog-for-claude
cd worklog-for-claude/mcp
uv sync
```

## Connect

Add to your MCP client config. Replace the path with the absolute path to this `mcp/` directory.

**Claude Code** — `.claude/settings.json`:
```json
{
  "mcpServers": {
    "worklog-mcp": {
      "command": "uv",
      "args": ["--directory", "/path/to/worklog-for-claude/mcp", "run", "worklog-mcp"]
    }
  }
}
```

**Cursor** — `~/.cursor/mcp.json` (same format)

**Claude Desktop** — `~/Library/Application Support/Claude/claude_desktop_config.json` (same format)

See `examples/` for complete config files.

## Tools

| Tool | Description |
|---|---|
| `write_worklog` | Append an entry to `.worklogs/YYYY-MM-DD.md` |
| `read_worklog` | Read worklog for a given date (default: today) |
| `write_worklog_to_notion` | Send worklog entry to Notion DB |
| `read_project_doc` | Read `PROJECT.md` with section parsing |
| `create_project_doc` | Create `PROJECT.md` with 7 standard sections |
| `analyze_gaps` | Compare recent git commits to `PROJECT.md`, return gaps |
| `update_project_doc` | Update a specific section (replace or append) |

## PROJECT.md Sections

```
## 이게 뭔가       — one-line description
## 왜 만들었나     — motivation and problem
## 구조            — folder/file structure
## 기술 스택       — tech choices and reasons
## 주요 결정들     — key architectural decisions
## 해결한 문제들   — bugs and how they were fixed
## 지금 상태       — current state, what works, what's next
```

## Notion Setup

Set environment variables before running the server:

```bash
export NOTION_TOKEN=secret_...
export NOTION_DB_ID=your-db-id
```

Or pass them directly as tool arguments.

Required Notion DB columns: `Title`, `Project`, `Cost`, `Duration`, `Model`, `Tokens`, `DateTime`

## Gap Detection

`analyze_gaps` watches your git history and finds what's missing in `PROJECT.md`:

- `feat:` commits → checks `주요 결정들`, `지금 상태`
- `fix:` commits → checks `해결한 문제들`
- `refactor:` commits → checks `구조`, `기술 스택`
- Empty sections → always flagged
- Recent `docs:` or `PROJECT.md` commit → skips gap check

## Test

```bash
uv run pytest tests/ -v
```

71 tests, all passing.
