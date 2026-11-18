# Frontend foundation validation

**Activity:** WBS-1.6. **Owner:** Abdullah Faruk Özbek. **Date:** 13 November 2026.
**Status:** Hasan approved the original draft on 12 November. Faruk approved publication of the 13 November review fixes. Hasan's follow-up review is pending.

## 1. Scope

These checks cover the frontend foundation and public empty previews.
They do not test login, portal integration, source processing or AI output.
They do not establish the full NFR-15 accessibility acceptance condition or NFR-14 usability score.
This note provides evidence for the future Test Spec. It is not the formal Test Spec submission.

## 2. Reproduce the checks

From `frontend/`:

```sh
npm ci
npm test
npm run typecheck:tests
npm run lint
npm run build
npx playwright install chromium
npm run test:browser
```

If Chromium is already installed, set `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` to its executable for the browser command.
The test server binds to `127.0.0.1:4173` and stops when the browser tests finish.
Traces for failed browser tests are under `tests/frontend/browser-results/`, which is not committed.

## 3. Cases and requirements

| Case | Check | Requirement |
|---|---|---|
| Component navigation | Student, teacher and administrator links stay in their preview role. | NFR-12; presentation part of FR-06 |
| Preview boundary | Login is disabled; entry links are clearly called previews. | Scope correctness; FR-02/FR-03 remain pending |
| Activation | Account activation is limited in its text to existing portal accounts. | FR-02 |
| Route change | Direct links work; heading receives focus; document title and active link update. | NFR-12, NFR-15 |
| Not found | Unknown routes show a recovery link. | NFR-12 |
| Shared input | Visible label, hint and error are connected programmatically. | NFR-15 |
| Responsive pages | All 12 routes have no horizontal overflow at 360, 768 and 1440 px. | NFR-13 |
| Automated accessibility | axe WCAG 2 A/AA and 2.1 A/AA scans on those routes and widths. | Partial evidence for NFR-15 |
| Phone menu | Keyboard opening, Escape, focus return, navigation, back and reload. | NFR-12, NFR-15 |
| Skip and zoom | Skip link focuses main content; 200% zoom with 360 effective CSS px; reduced-motion setting. | Partial evidence for NFR-13/NFR-15 |

## 4. Test-first record

The seven initial component tests were run against the original `App.tsx` before implementing the foundation.
All seven failed because the original page only displayed the title "Chiron".
The shared-input test was then added with the component.
Browser checks were added after the layout was implemented.
This distinguishes the initial test-first work from later regression checks.

## 5. Results

Environment: Linux, Node.js 24.19.0, npm 11.17.0 and Chrome 156.0.8078.47.
The team targets Node.js 22. A run on that version remains a CI handoff check.

| Command / inspection | Actual result |
|---|---|
| `npm test` | Passed: 9 component tests in 2 files. |
| `npm run typecheck:tests` | Passed. Root-level test imports resolve through `frontend/node_modules`. |
| `npm run lint` | Passed for frontend code and root-level frontend tests. |
| `npm run build` | Passed. JavaScript bundle approximately 271 kB, 86 kB gzip. |
| `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/google-chrome npm run test:browser` | Passed: 6 browser tests. |
| Responsive / axe scan | All 12 routes checked at 360, 768 and 1440 px. No horizontal overflow or violations from the selected WCAG A/AA rules were reported. |
| Phone keyboard flow | Menu open, Escape/focus return, route focus, back and reload passed. |
| Skip / zoom check | Main-content focus and 200% CSS zoom at an effective 360 px passed. Reduced-motion emulation was enabled. |
| Screenshot inspection | Login and student course layouts checked at desktop and phone sizes. |
| Additional design inspection | Login and student courses checked at 390, 820 and 1024 px after the skill-guided refinement. No horizontal overflow was found. Screenshots were visually inspected. |

The first browser run hit the runner's 30-second timeout because one test scans 12 pages with axe.
The timeout was raised to 120 seconds for that workload. The successful scans took about 47 seconds per width.
The first zoom case used a viewport below the supported effective width; the final check uses 720 physical CSS viewport px with 200% CSS zoom.

Screenshots of the implemented interface:

- [Login, desktop](../design/frontend-evidence/login-desktop.png)
- [Login, phone](../design/frontend-evidence/login-phone.png)
- [Student courses, desktop](../design/frontend-evidence/student-desktop.png)
- [Student courses, phone](../design/frontend-evidence/student-phone.png)

These are screenshots of empty previews, not evidence of completed backend features.

### Design refinement on 12 November

The revised draft uses blue navigation, larger supporting text, a horizontal desktop empty state and related-tool rows.
The entry page uses one joined introduction and form panel. On phones, the panel stacks vertically.
The route behavior and preview boundaries stay the same.
The source skills and the reasons for adapting their guidance are recorded in [the design note](../design/frontend-foundation.md#9-design-refinement-plan-and-review).
The project checks cover the revised application. Taste Skill's marketing-site checker was not run.

### Review fixes on 13 November

The new shell regression test failed before the fix because navigation replaced the menu button and sidebar.
It passes after removing the pathname key from `AppShell`.
The shell now resets only the disclosure state on a new location.
Same-page links and browser back/forward navigation also close the menu and preserve heading focus.

All nine component tests, test type checking, lint and build passed on the updated draft.
All six browser tests passed after the style-layer and layout changes.
The extended phone-menu test passed again after adding same-page and back/forward checks.
These are local results. No GitHub CI checks were registered on PR #39 at review time.

The styling follows the charter: Tailwind layout utilities plus shared component rules in its cascade layers.
Teacher and administrator copy now uses plain labels.
[Issue #43](https://github.com/Bur8300/Chiron/issues/43) tracks replacing or protecting public previews before authentication integration.

## 6. Remaining acceptance work

- Generate and verify the API client after WBS-1.1.
- Run Lighthouse on every finished page and record scores against the NFR-15 minimum of 90.
- Perform a manual keyboard-only walkthrough of the finished product, including forms and errors.
- Test with a screen reader and real phones after the feature pages exist.
- Conduct the NFR-14 SUS evaluation with at least five students. Do not infer a SUS score from automated tests.
- Verify secure login, role and assignment authorization through backend tests.
- Add real feature integration and end-to-end tests when their APIs exist.
- Review phone safe areas, file upload, PDF opening and secure storage inside Capacitor under WBS-12.

Automated accessibility results detect only a subset of accessibility problems.
An empty preview passing these tests does not certify the final application.
