# Chiron

Chiron is an AI-powered study assistant for EBA-like Turkish online education portals, developed as the BLG 411E Software Engineering term project. Students upload course sources, ask questions answered with citations to those sources, generate summaries (PDF compiled from LaTeX) and quizzes, and get a weekly study plan for their weakest topics. Teachers and administrators follow the performance and AI token usage of the students assigned to them. Chiron is used through a web application and a mobile application for Android and iOS built from the same frontend with Capacitor. Portal integration is demonstrated with a mock EBA adapter.

## Team — Forge of Hephaistos

| Member | Development role | Management role |
|---|---|---|
| Burak Emre Polat | Backend / DevOps Developer | Project Manager, Product Owner |
| Metin Furkan Amarat | Backend / RAG Engineer | Test Lead |
| Hasan Yalçın Arıkanoğlu | AI / Study Planner Engineer | Requirements Analyst |
| Berkay Türk | Full-stack Developer | QA / CI-CD & Configuration Manager |
| Abdullah Faruk Özbek | Frontend Developer | UX / Documentation Lead |
| AI Agent (Claude Code) | Code, test and documentation drafting | — |

The AI agent works only on branches through PRs and never commits directly to `main`; everything it produces is reviewed by a team member before merging.

## Documents

All documents are kept in [`docs/`](docs/):

| Deliverable | File | Release |
|---|---|---|
| Project Charter | [`docs/Charter.md`](docs/Charter.md) | `charter-v1.0` |
| Project Plan | [`docs/ProjectPlan.md`](docs/ProjectPlan.md) | `project-plan-v1.0` |
| Requirements Spec | `docs/RequirementsSpec.md` | `requirements-spec-v1.0` |
| Requirements Analysis | `docs/RequirementsAnalysis.md` | `requirements-analysis-v1.0` |
| Design Spec | `docs/DesignSpec.md` | `design-spec-v1.0` |
| Test Spec | `docs/TestSpec.md` | `test-spec-v1.0` |

## Technology

- **Backend:** Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL with pgvector, Redis job queue, pytest
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Vitest, Playwright
- **Mobile:** Capacitor (Android, iOS)
- **AI:** LiteLLM gateway, bge-m3 embeddings, PyMuPDF / Docling, Tectonic (LaTeX)
- **Infrastructure:** Docker, GCP (Cloud Run, Cloud SQL, Cloud Storage), GitHub Actions

## Workflow

- Every change goes through a branch and a PR to `main`; direct pushes to `main` are not allowed.
- Each document is written on its own `docs/<name>` branch and released from that branch by its deadline.
- Requests from customer meetings are recorded as issues with the `customer-requests` label within 48 hours.
- Tests live in the `tests/` folder.

## License

See [LICENSE](LICENSE).
