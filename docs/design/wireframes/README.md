# Login and student wireframes

**Activity:** WBS-11.3. **Issue:** [#32](https://github.com/Bur8300/Chiron/issues/32).
**Owner:** Abdullah Faruk Özbek. **Reviewer:** Hasan Yalçın Arıkanoğlu.
**Date:** 13 November 2026. **Status:** Proposed layouts for review.

## Scope and prototype

This first slice covers login, account activation and the student pages.
Teacher and administrator wireframes remain pending for W6 in the recovery plan.
The full issue is not complete. A PR for this slice must say `Refs #32`.

Open the [clickable navigation prototype](index.html) locally.
GitHub's file view shows its source, not the running prototype.
From this folder, run `python3 -m http.server 4174 --bind 127.0.0.1` and open `http://127.0.0.1:4174`.
Choose a screen, then choose desktop or phone.
The prototype changes screens; it does not implement login, uploads, questions or quizzes.
An externally hosted prototype URL remains a handoff item if required by the reviewer.

The image exports are SVG, so they remain sharp when zoomed.
Run `python3 generate.py` to recreate them from the reviewed screen definitions.

## Screen inventory

| Screen | Use case / requirements | Desktop | Phone |
|---|---|---|---|
| Login | UC-01; FR-03 to FR-06 | [Image](login-desktop.svg) | [Image](login-phone.svg) |
| Account activation | UC-01; FR-02 | [Image](activation-desktop.svg) | [Image](activation-phone.svg) |
| Courses | UC-03; FR-10 | [Image](courses-desktop.svg) | [Image](courses-phone.svg) |
| Sources | UC-04; FR-13 to FR-17 | [Image](sources-desktop.svg) | [Image](sources-phone.svg) |
| Questions and citations | UC-05; FR-18 to FR-20, FR-37 | [Image](questions-desktop.svg) | [Image](questions-phone.svg) |
| Summary | UC-06; FR-21, FR-25 | [Image](summaries-desktop.svg) | [Image](summaries-phone.svg) |
| Quiz and results | UC-07; FR-22 to FR-25 | [Image](quiz-desktop.svg) | [Image](quiz-phone.svg) |
| Weekly plan | UC-08; FR-27 to FR-31 | [Image](planner-desktop.svg) | [Image](planner-phone.svg) |

UC-11 and UC-12 are backend/background flows, not separate student screens.
UC-13 uses the same flows on phones. Native file selection, PDF opening and secure token storage need the mobile design owners' decisions.

## Navigation and accessibility rules

- Keep the selected course visible while moving between its study tools.
- Use a sidebar on desktop and a labelled expandable menu on phones.
- Use one main heading, a main content landmark and a skip link.
- Move focus to the main heading after navigation. Update the browser title.
- Give each field a visible label. Associate hints and errors with that field.
- Use radio groups for quiz choices. Do not communicate selection or correctness by color alone.
- Keep interactive targets at least 44 CSS px. Keep text and controls within a 360 px viewport.
- Make citations keyboard accessible. Name the source and page in the link.
- Retain input when validation fails. Announce errors and long job status changes accessibly.
- Show confirmation before deleting a source. Return focus to a sensible location after a dialog closes.
- Respect reduced motion. Avoid interaction that requires dragging or hovering.

## States to review

Each export contains an alternative/error-state note.
The implementation must cover loading, empty, success and failure states where applicable.
The source screen must distinguish processing, ready and failed sources.
The question screen must handle no answer in sources and token limit/reset date.
Summary and quiz screens must show job status and failure after the specified timeout.
Quiz answers and citations appear only after submission.
The planner must show why a topic is weak and the date of the grades used.

The wireframes do not define new password thresholds, API endpoints or an unanswered-quiz policy.
Those decisions must be agreed with the relevant owners.
DOCX and PPTX are Should scope in FR-14; PDF is the Must baseline.

## Submission and review

These are design inputs for `docs/DesignSpec.md`, not a formal report release.
The supplied Project Submission and Tracking Guide says the grade uses the released report version.
The report owners must include the reviewed diagrams and decisions in that submission.
Issue #32 lists 22 November; the recovery brief targets this student/login slice by 20 November.
Confirm the schedule with Burak instead of silently changing it.

Codex drafted these wireframes and notes from Requirements Specification v1.0.
Faruk reviewed the original draft before publication. Hasan approved PR #41 on 12 November and left follow-up comments.
Faruk approved publication of the 13 November revisions. Hasan's follow-up review is pending.
No usability study, SUS score or customer approval is claimed.

## Validation

All 16 SVG exports loaded in Chrome on 12 November 2026.
The prototype's eight screen links and both size selectors were checked in a browser.
The source-page desktop and phone exports were also visually inspected.
This checks the artifact files and navigation, not student usability or final feature behavior.

## Review fixes on 13 November

- Login uses FR-03 to FR-06 in both the generator and the manifest. Activation keeps FR-02.
- The quiz screen cites FR-25 and states that a generation error has a message and a retry action.
- The planner states that a student with no weak topics can try a quiz from their sources (UC-08 A1).
- Sources show a course selector, upload button, selection controls and ready, processing and failed rows.
- Questions show a labelled question field, send button, answer, source/page citation and passage.
- The planner shows a desktop table and stacked phone entries with success rates, hours and study steps.

The sample filenames, answer and passage only show the proposed layout. They are not real sources or AI output.
The planner's sample rates and topics follow the UC-08 acceptance scenario. Hours follow the FR-29 note.
Controls inside the SVG images are drawings. The HTML prototype provides screen navigation only.
Teacher and administrator screens remain outside this slice.

All 16 exports loaded in Chrome on 13 November. Both sizes of all eight screens passed navigation checks.
Browser checks found no text outside the SVG canvas. Sources, questions and planner were visually inspected at both sizes.
The question-page footer overlap found during inspection was corrected.
The generator reproduces the checked-in SVG and manifest files exactly.
These checks do not replace the student usability study.
