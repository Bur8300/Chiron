# Frontend foundation

| Field | Value |
|---|---|
| Activity | WBS-1.6, T-01, D-03 |
| Issue | [#18](https://github.com/Bur8300/Chiron/issues/18) |
| Owner | Abdullah Faruk Özbek |
| Reviewer | Hasan Yalçın Arıkanoğlu |
| Draft date | 12 November 2026 |
| Status | Draft for team review. API client blocked by WBS-1.1. |

## 1. Purpose and scope

This change extends the React, Vite and TypeScript skeleton merged in PR #38.
It adds navigation, shared components, Turkish text and layouts for desktop and phone screens.
It provides empty preview pages for the student, teacher and administrator roles.
It does not implement authentication, portal data, uploads or AI features.

The main inputs are `docs/ProjectPlan.md` version 1.1 and Requirements Specification version 1.0 on `docs/requirements-spec`.
The supplied RequirementsSpec.pdf has the submission date 8 November 2026.
This note supports the later Design Spec. It is not a replacement for the formal Design Spec release.

## 2. Requirement traceability

| Requirement | Foundation contribution | Evidence and limit |
|---|---|---|
| NFR-11 | All application text is in Turkish. | `frontend/src/i18n/tr.ts`; future generated answers are not implemented. |
| NFR-12 | Each role has its own navigation and page titles. | Route tests and keyboard browser test. |
| NFR-13 | Responsive layout starts at 360 px. | Browser checks at 360, 768 and 1440 px. |
| NFR-15 | Labels, focus handling, skip links, contrast and keyboard navigation. | Automated axe and keyboard checks. Lighthouse and a manual assistive-technology review are still required for full acceptance. |
| FR-02, FR-03 | Separate account activation and login layouts. | Disabled preview fields. No credentials are collected. Authentication is future WBS-2.3/WBS-2.4 work. |
| FR-06, FR-07 | Navigation contains only the functions of its preview role. | This is presentation only. API authorization and assignment checks are not implemented. |
| FR-10 | Student course-page placeholder. | No portal requests or invented course data. |
| FR-13 to FR-23 | Source, question, summary and quiz placeholders. | Copy reflects the specified flows. No feature is claimed complete. |
| FR-27 to FR-34 | Study-plan and monitoring placeholders. | No grades, plans or usage totals are fabricated. |
| FR-08, FR-09, FR-12 | Administrator account-management placeholder. | No account mutation is possible. |
| NFR-26 | Contract-first API integration remains a dependency. | No `contracts/openapi.yaml` exists on the inspected main revision, `e7f2398`. No endpoints are invented. |

## 3. Structure

| Path | Responsibility |
|---|---|
| `frontend/src/app/routes.ts` | Role and route definitions. |
| `frontend/src/app/AppShell.tsx` | Desktop sidebar, phone menu, preview notice and content landmark. |
| `frontend/src/pages/EntryPage.tsx` | Login and account activation previews. |
| `frontend/src/pages/StudyPage.tsx` | Empty role pages with navigation to related areas. |
| `frontend/src/components/` | Brand, icons, labelled input and empty state. |
| `frontend/src/i18n/tr.ts` | Shared Turkish interface text. |
| `frontend/src/index.css` | Shared colors, typography, spacing and responsive rules. |
| `tests/frontend/` | Component and browser tests. |

React Router handles page URLs and browser history.
The production host must return `index.html` for frontend paths.
Backend API paths must remain separate from that fallback.

## 4. Navigation

All role pages use `/onizleme/` to show that they are public previews.
No browser storage contains a session or role claim.
When authentication is implemented, the team must replace the preview entry flow and enforce access on every API request.
Hiding a navigation link is not an authorization control.

| Route | Role / use case |
|---|---|
| `/giris` | All roles; UC-01 |
| `/hesap-etkinlestir` | Existing portal accounts only; UC-01 |
| `/onizleme/ogrenci/dersler` | Student; UC-03 |
| `/onizleme/ogrenci/kaynaklar` | Student; UC-04 |
| `/onizleme/ogrenci/soru-cevap` | Student; UC-05 |
| `/onizleme/ogrenci/ozetler` | Student; UC-06 |
| `/onizleme/ogrenci/sinavlar` | Student; UC-07 |
| `/onizleme/ogrenci/calisma-plani` | Student; UC-08 |
| `/onizleme/ogretmen/ogrenciler` | Teacher; UC-09 |
| `/onizleme/yonetici/ogrenciler` | Administrator; UC-10 |
| `/onizleme/yonetici/hesaplar` | Administrator; UC-02 |

UC-11 and UC-12 are service/background flows, not extra pages.
UC-13 reuses these pages on a phone.
Unknown URLs have a recovery link to the login page.

## 5. Interface decisions

- Use white content surfaces, blue navigation and a navy text color. The proposed palette needs team review.
- Use system fonts. The app does not request fonts from a third party.
- Keep one primary heading per page. Move focus to it after navigation.
- Give each route a unique browser title and mark the active navigation link.
- Below 761 px, replace the sidebar navigation with an inline expandable menu.
- The menu button exposes its expanded state. Escape closes it and returns focus to the button.
- Close the menu when the route changes. It is not a modal and does not trap focus.
- Use native links, buttons, inputs and labels. Decorative icons are hidden from assistive technology.
- Disable motion transitions when reduced motion is requested.
- Show an explicit preview notice. Do not display fake grades, tokens or learning progress.

## 6. API dependency and completion gate

WBS-1.6 is not complete until its API client is generated from the agreed contract.
Burak leads WBS-1.1 in issue #10, with Metin and Berkay in #11 and #12.

After the contract is merged:

1. Agree the generator and output location with the API owners.
2. Generate the client from `contracts/openapi.yaml`. Do not hand-edit generated files.
3. Add a reproducible generation command and a drift check.
4. Connect the client through an application adapter. Define error, cancellation and loading behavior from the contract.
5. Add contract-based tests with mocked responses.
6. Re-run the checks and ask Hasan to review the completed issue.

Until then, a PR for this slice must say `Refs #18`, not claim that #18 is complete.
The issue remains open. The team can split the remaining client work into a linked issue if it agrees.

## 7. Review and handoff

The WhatsApp recovery brief targets 13 November for WBS-1.6.
The current issue still lists 1 November. Burak must reconcile the schedule with the team.
This change does not silently change either deadline.

Hasan reviews Faruk's PR. Berkay owns the CI integration.
The foundation adds a separate test type-check command because PR #38's review found that root-level frontend tests were not type-checked.
The CI owner can call this command from the pending CI branch.

See [validation](../testing/frontend-foundation.md) for commands, results and remaining checks.
The official report owners can reuse the route table, decisions and evidence in `docs/DesignSpec.md` and `docs/TestSpec.md`.

## 8. AI contribution

Codex drafted the interface, tests and this design note from the project documents.
UI/UX Pro Max, Anthropic Frontend Design and Taste Skill supplied design guidance.
They were the first three Design entries shown on [Skill Issue](https://skill-issue.in/) on 12 November 2026.
The selected layout is an application workspace. The marketing-page pattern returned by the first search was not used.
Faruk must review the draft and be able to explain it before pushing, as required by `AGENTS.md`.
No human review, merge, release or grade is claimed here.

## 9. Design refinement plan and review

The product is a Turkish study application for students, teachers and administrators.
The draft must show the planned study areas and clearly identify its public previews.
The main interaction is navigation between those areas. Login remains disabled until its API is available.

### Sources and use

| Skill | Applied guidance |
|---|---|
| [UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | Use an accessible, flat learning workspace. Keep visible focus, readable contrast, responsive navigation and large touch targets. |
| [Frontend Design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) | Set a coherent palette and type scale before styling. Remove repeated uppercase labels. Use hierarchy and spacing to distinguish content. Inspect screenshots. |
| [Taste Skill](https://github.com/Leonxlnx/taste-skill/blob/main/skills/taste-skill/SKILL.md) | Use shared tokens, equal content edges, plain Turkish labels and restrained interaction feedback. Do not invent statistics or results. |

Taste Skill version 2.5.1 mainly targets marketing websites.
Its full-screen sales sections, shader effects, random layout selection and marketing checker do not fit this application task.
Its instruction to remove preview labels also conflicts with this draft's scope.
Those parts are not applied. The existing React components and project browser tests remain the implementation and validation tools.
No result from Taste Skill's marketing gate is claimed.

### Tokens and layout

| Token | Proposed value / purpose |
|---|---|
| Ink | `#172b43`: headings and body text |
| Muted | `#52627a`: supporting text |
| Primary | `#245ac7`: links, focus and selected navigation |
| Navigation | `#163858`: the workspace sidebar and entry introduction |
| Canvas | `#f3f6fa`: the page background |
| Surface | `#ffffff`: the form and content areas |

Use the device's sans-serif font for the Turkish interface. Do not request external fonts.
Use 16 px body text, 13–14 px supporting labels and a responsive heading scale.
Align the entry introduction beside the form on desktop. Stack them on a phone.
Keep the desktop navigation separate from the reading area.
Use a compact empty state and a list of related tools instead of three equal feature cards.

```text
Entry:      [ introduction      | account form ]
            [ role preview links              ]
Workspace:  [ navigation | page heading         ]
            [            | empty state          ]
            [            | tool heading | links ]
Phone:      [ brand and menu                    ]
            [ notice, heading and empty state   ]
            [ tool links                        ]
```

The plan review rejected a marketing hero and decorative charts because the project has no live study data yet.
The visual emphasis is the blue navigation area. The study content uses quiet surfaces and consistent edges.
This is a proposed refinement for Faruk and Hasan to review. It changes no feature acceptance criteria.
