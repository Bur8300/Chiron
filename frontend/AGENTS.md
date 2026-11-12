# Frontend rules

Read the root `AGENTS.md` first.

## Scope

This folder contains the React, TypeScript and Vite application.
Use `src/app/` for routing and the app shell.
Use `src/pages/` for pages and `src/components/` for shared controls.
Keep interface text in `src/i18n/tr.ts`. Do not write Turkish labels inside components.
Keep code comments and documentation in English.

## Interface

- Follow the FR, NFR and UC IDs in the Requirements Specification.
- Support screens from 360 px wide.
- Use semantic HTML, visible labels, keyboard navigation and visible focus.
- Update the browser title and focus when the route changes.
- Keep decorative icons out of the accessibility tree.
- Respect reduced motion.
- Use shared style tokens. Document new interface decisions in `docs/design/`.
- Do not collect credentials or show student data in the public `/onizleme/` routes.
- Never treat client-side navigation as authorization. The API must enforce access.

## API and tests

- Generate the API client from the agreed `contracts/openapi.yaml` after WBS-1.1.
- Do not invent endpoints or hand-edit generated client files.
- Put all tests under the root `tests/frontend/` folder.
- Run `npm test`, `npm run typecheck:tests`, `npm run lint` and `npm run build` from this folder.
- Run `npm run test:browser` for routing, responsive layout or accessibility changes.
- Record actual results and pending acceptance checks in the PR. Do not claim unrun checks passed.
