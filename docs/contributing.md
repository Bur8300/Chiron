# Contributions and course submissions

This guide summarizes the supplied BLG 411E Project Submission and Tracking Guide.
It helps the team follow the submission process. It does not replace the instructor's announcements or a deliverable's content checklist.
Exact deadlines are announced separately.

## 1. Individual work

1. Check that your Git email is linked to your own GitHub account.
2. Find your assigned issue. Keep its status current on the project board.
3. Work on a branch. Use `<type>/wbs-<id>-<short-name>` for activity work.
4. Read the code and documents drafted by an AI agent. Be able to explain them.
5. Run the checks that apply to the change. Record commands, results and limits in the PR.
6. Push from your account and open your own PR to `main`.
7. Include `Closes #N` when the PR completes the issue. Use `Refs #N` for an incomplete slice and explain the remaining work.
8. Ask the assigned teammate to review. Faruk and Hasan review each other's work.
9. After approval, the PR author merges with a merge commit. Do not squash.

The course assesses individual contributions from GitHub records and Peer Scoring.
Commit count alone is not the measure. Reviews also count.
Do not claim a review or approval that has not happened.

## 2. Document submissions

The grade is based on the version in the release published by the deadline.
A PR alone is not a submission.

| Document | Branch | File | Release |
|---|---|---|---|
| Project Charter | `docs/charter` | `docs/Charter.md` | `charter-v1.0` |
| Project Plan | `docs/project-plan` | `docs/ProjectPlan.md` | `project-plan-v1.0` |
| Requirements Spec | `docs/requirements-spec` | `docs/RequirementsSpec.md` | `requirements-spec-v1.0` |
| Requirements Analysis | `docs/requirements-analysis` | `docs/RequirementsAnalysis.md` | `requirements-analysis-v1.0` |
| Design Spec | `docs/design-spec` | `docs/DesignSpec.md` | `design-spec-v1.0` |
| Test Spec | `docs/test-spec` | `docs/TestSpec.md` | `test-spec-v1.0` |

Before the deadline:

- Open a PR from the prescribed document branch to `main`. A draft PR can be opened early.
- Obtain at least one teammate's approval before requesting TA review.
- Publish the named release with the PR branch as the target, not `main`.
- Open the release page and verify that the submitted document is included.
- Add the TA as a reviewer.

The project rules reserve merges and releases for a team member, not the AI agent.
Design notes in `docs/design/` and validation notes in `docs/testing/` support the formal reports.
They do not replace those reports or their releases.

## 3. Revision after TA feedback

1. Fix feedback in the same PR. Do not open a replacement PR.
2. Reply to each comment with the change made. Resolve inline conversations after the fix.
3. If the feedback is a review summary without an inline thread, reply in the PR discussion.
4. If you disagree, explain why before resolving the comment.
5. Merge after all feedback is addressed, by the next deliverable's deadline. The course guide does not require another TA approval at this point.

Later PR commits do not change the v1.0 grade.
Do not delete and recreate a release: that changes its publication time.
TA approval of a PR is not a grade.

## 4. Evidence to keep with work

- Explain the trigger, change and resulting behavior.
- Link the issue, WBS ID and relevant FR, NFR or UC IDs.
- State what is complete and what depends on other work.
- Keep documents in `docs/` and tests in `tests/`.
- Record actual test results. Separate automatic checks from manual review.
- Put interface decisions and navigation rules in the design notes.
- Keep screenshots of the real interface separate from proposed wireframes.
- Record the AI tool and drafted parts honestly. Report only Chiron token usage.

Use short sentences and consistent terms, as required by `AGENTS.md`.
Preserve the IDs in the approved project documents.

## 5. Customer requests and final submission

Open a separate issue with the exact label `customer-requests` for each customer request within 48 hours.
Record the meeting, the request in your own words and acceptance criteria.
Link completion through the implementing PR. If deferred or declined, record the reason and close as not planned.

The guide sets the final code freeze to 25 December, with release `v1.0.0` on `main`.
The 26 December demo uses that release.
Check the course announcements for the precise deadline times.
