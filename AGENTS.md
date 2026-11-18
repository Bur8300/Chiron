# AGENTS.md — Chiron

This file gives the rules for all AI agents and all team members who work in this repository.
Read this file before you start a task.

## 1. About Chiron

Chiron is an AI study assistant for EBA-like Turkish online education portals.
Students upload course sources and ask questions. Chiron answers with citations to the sources.
Students also generate summaries (PDF) and quizzes, and get a weekly study plan for their weakest topics.
Teachers and administrators monitor the performance and AI token usage of their assigned students.

Read these documents for the full scope:

- [Project Charter](docs/Charter.md)
- [Project Plan](docs/ProjectPlan.md)
- Requirements Specification: `docs/RequirementsSpec.md`. Until PR #7 is merged, read it with `git show origin/docs/requirements-spec:docs/RequirementsSpec.md`.

## 2. Architecture decisions

The team made these decisions. Do not change them without a team decision.

- **One backend code base.** The API and the background worker run from the same code as two processes.
- **The AI code is a module of the backend** (`backend/app/ai/`). It is not a separate service.
- **Contract-first API.** The team writes `contracts/openapi.yaml` by hand first. The backend and the frontend follow it. To change an endpoint, change `contracts/openapi.yaml` first, in the same PR or in an earlier PR.
- **All tests are in `tests/`.** The course guide requires this. Do not put tests in `backend/` or `frontend/`.
- **Tasks are GitHub issues.** There is no separate task file. Each task issue has one assignee, a board status and a WBS ID.

## 3. Repository structure

```
Chiron/
  AGENTS.md            Rules for all AI agents and people
  CLAUDE.md            Tells Claude Code to read AGENTS.md
  README.md
  docs/                Course documents
    design/            Design notes (architecture, database, RAG, gateway, portal data, mobile, wireframes)
  contracts/           openapi.yaml (API contract)
  backend/             FastAPI application and background worker
    app/api/           REST endpoints
    app/services/      Auth, portal adapter, sources, planner, dashboard
    app/ai/            LLM gateway, RAG, summary and quiz generation
    app/worker/        Background jobs (Redis)
    alembic/           Database migrations
  frontend/            React + Vite; Capacitor android/ and ios/
  infra/               Dockerfiles, docker-compose, GCP deployment
  tests/
    backend/ frontend/ e2e/ mobile/ security/ performance/ evaluation/
  .github/             Workflows, issue templates, PR template
```

Some folders do not exist yet. The team adds them in W4 and W5.

Before you change files in a folder, read the `AGENTS.md` file in that folder.

## 4. Work flow

1. Find your issue: `gh issue list --assignee @me`.
2. Move the issue to "In Progress" on the board.
3. Create a branch from `main`. Use the branch name rules in section 5.
4. Do the work. Keep the change in the scope of the issue.
5. Run the tests before you push.
6. Open a PR to `main`. Use the PR template.
7. Write `Closes #<issue number>` in the PR description.
8. Move the issue to "In Review".
9. Ask your reviewer for a review (see the review pairs in section 6).
10. The PR author merges the PR after one approval from the reviewer. Use a merge commit. Do not use squash.
    For a course document, merge only after all TA comments are resolved.

## 5. Branch names

Use this format: `<type>/wbs-<id>-<short-name>`.

- Write the WBS ID with hyphens. For example, WBS-1.3 becomes `wbs-1-3`.
- Use one of these types: `feat`, `fix`, `test`, `docs`, `chore`, `ci`, `refactor`.
- Example: `feat/wbs-1-3-scaffolding`.

Course documents use the branch names from the course guide:

| Document | Branch | File | Release |
|---|---|---|---|
| Requirements Analysis | `docs/requirements-analysis` | `docs/RequirementsAnalysis.md` | `requirements-analysis-v1.0` |
| Design Spec | `docs/design-spec` | `docs/DesignSpec.md` | `design-spec-v1.0` |
| Test Spec | `docs/test-spec` | `docs/TestSpec.md` | `test-spec-v1.0` |

For a course document, create the release with the PR branch as the target. Do not use `main` as the target.

Revision of a course document:

- Fix the TA comments in the same PR. Do not open a new PR.
- Reply to each comment with the change you made. Then click "Resolve conversation".
- If you do not agree with a comment, reply with your reason before you resolve it.
- Merge the PR before the deadline of the next document.
- Do not delete a release and create it again. This changes the publication time.

## 6. Rules

- Do not commit to `main`. Use a branch and a PR.
- Each PR needs one approval from a team member before merge.
- Put all tests in `tests/`.
- Write the tests before the code (test first). A feature PR without tests is not complete.
- Put all documents in `docs/`. Put design notes in `docs/design/`.
- Use your own GitHub account for your commits, PRs and reviews.
- Keep the board up to date: Todo, In Progress, In Review, Done.
- Keep API keys and other secrets out of the code. Use environment variables or GCP secrets.
- Do not use real student data. Use only the mock portal data.
- Open one issue with the `customer-requests` label for each customer request, in 48 hours after the meeting.
- In a customer request issue, write the request in your own words, the acceptance criteria and the meeting.
- Close a customer request only through a PR with `Closes #<issue number>`. If the team defers or declines a request, write the reason in the issue and close it as "not planned".

Review pairs:

| Author | Reviewer |
|---|---|
| Burak | Metin |
| Metin | Berkay |
| Berkay | Burak |
| Hasan | Faruk |
| Faruk | Hasan |

If your reviewer is not available for 24 hours, ask another member.

## 7. Rules for AI agents

The first three rules come from the Project Charter. The team added the other rules.

- The AI agent works only on branches and through PRs.
- The AI agent never commits to `main`.
- A team member reviews, verifies or corrects all output of the AI agent before merge.
- The team member who pushes AI output must read it first. That member must be able to explain it in a meeting.
- The AI agent does not merge PRs. It does not create releases.
- The AI agent shows each draft to the team member before it commits the draft.
- The AI agent does not invent requirements, thresholds or IDs. It uses the IDs from the Requirements Specification (FR-##, NFR-##) and the Project Plan (T-##, D-##, WBS-#.#).
- If a decision is not in the documents, the AI agent asks the team member. It does not guess.

## 8. Writing rule

Write all documents, issues, PR descriptions and `AGENTS.md` files in Simplified Technical English:

- Use short sentences.
- Use the active voice.
- Write one instruction in each sentence.
- Use the same term for the same thing in all documents.

Code, comments and commit messages are in English.

## 9. AI token usage

The course asks each member to report the use of AI agent tools in tokens.

- Add `"cleanupPeriodDays": 365` to `~/.claude/settings.json`. If you do not, Claude Code deletes local logs after 30 days. If you use another tool, find the same setting in that tool.
- Use Chiron only in its own folder. This keeps the project sessions separate from your other projects.
- Every Friday, run `npx ccusage@latest daily` (or Tokscale) and send the result to Burak.
- If your tool keeps usage only online, use the usage page of your account.
- Report only Chiron sessions. Report all use honestly. A high number is not a failure, and a low number is not a success.
