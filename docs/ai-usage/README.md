# AI Token Usage Reports

The course asks each member to report the use of AI agent tools in tokens.
This folder has one file for each week. Each file has the usage of all members in that week.

## Rules

- A week is Monday to Sunday. The week numbers are the numbers of the Project Plan (W0 starts on 12.10.2026).
- The file of a week is `week-<date of the Monday>.md`.
- Every Friday, each member adds their usage of the week to the file of the week. Use your own GitHub account (`AGENTS.md` section 6).
- Add one row for each topic. Use one topic from the list below. Write the WBS IDs or the task in "Details".
- Report all columns: API calls, input, cache write, cache read, output and total. Total = input + cache write + cache read + output.
- Report only the work on Chiron. Do not report other courses or other projects.
- Report all tools that you used. Write the tool in the "Tool" column (for example Claude Code, Codex, claude.ai). If a tool does not show a column, write "—".
- If you did not use an AI tool in a week, write "No use this week" and 0.
- Update the "Project total" table below and your total in the file of the week.

## Topics

| Topic | Examples |
|---|---|
| Documentation | Charter, Project Plan, Requirements Specification, Requirements Analysis, Design and Test Specification, README |
| Project management | Issues, board, briefings, `AGENTS.md`, meeting notes, token reports (WBS-11.8) |
| Backend | API contract, database, services, portal adapter |
| Frontend | Pages, components, wireframes, mobile application |
| AI | RAG, LLM gateway, summary, quiz and study plan generation |
| DevOps/CI | Repository setup, CI, Docker, deployment |
| Testing | Test infrastructure, unit, integration, end-to-end and evaluation tests |
| Code review | Reviews of pull requests (WBS-10.1) |

## How to measure

Claude Code keeps local logs. Set `"cleanupPeriodDays": 365` in `~/.claude/settings.json`, or Claude Code deletes logs after 30 days.

1. Run `npx ccusage@latest daily --since <Monday> --until <Sunday>` (dates as `YYYYMMDD`). It gives the usage of each day.
2. Use only the days and the sessions of the Chiron folders. `npx ccusage@latest session` shows the usage of each project folder.
3. Split the usage into topics by the work that you did in each session.

For another tool, use the usage page of the tool or of your account.

Cache reads are usually more than 90% of the total. Claude Code sends the whole conversation again on every call, and the API reads it from the cache. This is normal. Report it.

## Project total

The table shows the total tokens of each member for each week. Update it when you add your usage.

| Week | File | Burak | Metin | Hasan | Berkay | Faruk |
|---|---|---:|---:|---:|---:|---:|
| Before W0 (charter) | [week-2026-10-05.md](week-2026-10-05.md) | 6,415,512 |  |  |  |  |
| W0 | [week-2026-10-12.md](week-2026-10-12.md) | 0 |  | 9,600,000 |  |  |
| W1 | [week-2026-10-19.md](week-2026-10-19.md) | 94,928 |  | 110,600,000 |  |  |
| W2 | [week-2026-10-26.md](week-2026-10-26.md) | 0 |  |  |  |  |
| W3 | [week-2026-11-02.md](week-2026-11-02.md) | 36,541,765 |  | 78,500,000 | 11,263,064 |  |
| W4 | [week-2026-11-09.md](week-2026-11-09.md) | 9,517,141 | 1,496,791 |  | 3,102,208 | 35,501,270 |
| W5 | [week-2026-11-16.md](week-2026-11-16.md) | 39,077,947 | 1,145,140 |  |  |  |
| **Total so far** | | **91,647,293** | **2,641,931** | **198,700,000** | **14,365,272** | **35,501,270** |
