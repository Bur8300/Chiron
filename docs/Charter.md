# Project Charter: Chiron

## 1. Project Purpose and Objectives
Chiron is an AI-powered study assistant for EBA-like Turkish online education portals. Portal integration is demonstrated through a mock EBA adapter rather than the official EBA platform. Inspired by Google's NotebookLM, it lets students upload course sources, ask questions answered with citations to those sources, and generate study material as PDF documents compiled from LaTeX, starting with summaries. An "AI Counselor" ranks each student's subjects by success rate and gives short, encouraging advice on the topics they struggle with most, while teachers and administrators monitor the performance and AI token usage of the students assigned to them.

## 2. Stakeholders & Roles
* **Product Owner:** Burak Emre Polat
* **Software Engineering Team:** 
    * Burak Emre Polat : Backend / DevOps Developer (Tech), Project Manager (Mgmt)
    * Metin Furkan Amarat : Backend / RAG Engineer (Tech), Test Lead (Mgmt)
    * Hasan Yalçın Arıkanoğlu : AI / Counselor Engineer (Tech), Requirements Analyst (Mgmt)
    * Berkay Türk : Full-stack Developer (Tech), QA / CI-CD & Configuration Manager (Mgmt)
    * Abdullah Faruk Özbek : Frontend Developer (Tech), UX / Documentation Lead (Mgmt)
* **GH Repo/Project URL:** https://github.com/Bur8300/Chiron

## 3. Project Scope
### Project domain
Online education, specifically Turkish K-12 and secondary education delivered through portals such as EBA. As a hypothetical application, Chiron plugs into an EBA-like portal through a mock adapter. Possible customers are educational institutions and portal operators. Key users are students (source-grounded study, generated study material, counseling), teachers (performance and token usage of their assigned students in the subject they teach) and administrators (performance and token usage of their assigned students across all subjects).

### In-Scope 
* **Authentication & Authorization (Must-have):** Account management and role-based access control for students, teachers and administrators.
* **EBA Mock Adapter (Must-have):** A portal integration layer that serves mock EBA data (courses, units, content and student grades), keeping the system decoupled from a real portal.
* **Source Upload & Cited RAG Q&A (Must-have):** Uploading documents (e.g. PDF) and answering questions grounded in them, with citations to the source passages.
* **Summary Generation as PDF (Must-have):** Generating summaries of the selected sources as LaTeX code and compiling them into downloadable PDF documents.
* **Additional Study Material Formats (Stretch):** Generating further formats such as flashcards, each through its own generation pipeline ("skill"), kept only if the output proves reliable.
* **AI Counselor (Must-have):** Computing each student's per-subject success/failure rate from the portal grades with SQL queries, ranking subjects by success rate, and producing a short LLM-generated message with generic advice and encouragement to focus on the weakest subjects.
* **Teacher/Admin Dashboard (Must-have):** Students are assigned to teachers and administrators, and teachers are assigned to administrators. Teachers and administrators see the AI token usage of their assigned students; teachers see their students' performance in the subject they teach, and administrators see their students' performance across all subjects.
* **Multi-model LLM Gateway (Must-have):** A unified layer to call multiple LLM providers with fallback and cost control, recording per-student token usage.
* **Cloud Deployment & CI/CD (Must-have):** Hosting the services in the cloud with automated build, test and deploy pipelines.

### Out-of-Scope 
* Real integration with the official EBA platform
* Multimodal output generation: short-form video, audio overviews and PPTX presentations
* Native mobile applications
* Training or fine-tuning of custom models
* Languages other than Turkish and English

## 4. Technology Stack

### Backend Stack
* Python, FastAPI
* SQLAlchemy and Alembic
* PostgreSQL with pgvector
* Redis and a background job queue for long-running generation tasks
* JWT-based authentication and role-based authorization
* pytest
* Docker
* GCP: Cloud Run, Cloud SQL, Cloud Storage
* GitHub Actions (CI/CD)

### Frontend Stack
* React, TypeScript, Vite
* Tailwind CSS
* Vitest and Playwright

### AI Stack
* LiteLLM as the multi-model LLM gateway, with multiple cloud LLM providers and token usage tracking
* Multilingual embedding model (e.g. bge-m3) for Turkish and English content
* PyMuPDF / Docling for document parsing
* LaTeX (e.g. Tectonic) to compile LLM-generated study material into PDF
* Mocked LLM calls and a small evaluation dataset for deterministic tests

## 5. Project Milestones
| Deliverable                       | Deadline          |
|---                                |---                |
| Project Charter                   | 05.10.2026 23:59  |
| Project Plan                      | 19.10.2026 23:59  |
| Requirement Specification Report  | 02.11.2026 23:59  |
| Requirement Analysis Report       | 23.11.2026 23:59  |
| Software Design Report            | 07.12.2026 23:59  |
| Software Test Report              | 21.12.2026 23:59  |
| Codebase                          | 25.12.2026 23:59  |
| Demo                              | 26.12.2026 23:59  |
| Presentation                      | 28.12.2026 23:59  |
