# Manual QA checklist

Use this checklist after a meaningful UI or behavior change.

## First run and profile

- [ ] Fresh browser shows onboarding.
- [ ] Empty name is rejected with a clear message.
- [ ] A valid display name opens the dashboard.
- [ ] Refresh keeps the profile and entries.
- [ ] Logout asks for confirmation before erasing data.

## Daily workflows

- [ ] Add, complete, and delete a task.
- [ ] Add and complete a habit; verify today's completion state.
- [ ] Add a goal and adjust its progress.
- [ ] Add a transaction and verify totals.
- [ ] Create a note and journal entry.
- [ ] Start and finish a focus session.
- [ ] Add an event and verify its displayed date.

## Responsive and accessible use

- [ ] Check at 320px, 375px, 768px, 1024px, and desktop widths.
- [ ] No horizontal overflow on the dashboard.
- [ ] Header actions do not overlap.
- [ ] Bottom navigation remains usable on narrow screens.
- [ ] Keyboard focus is visible and buttons have understandable names.
- [ ] Dark and light themes both remain legible.

## Release checks

- [ ] Run `npm ci` and `npm run build` in `frontend`.
- [ ] Confirm the frontend CI workflow passes.
- [ ] Confirm the GitHub Pages deployment succeeds.
- [ ] Open the live URL and smoke-test the changed behavior.
