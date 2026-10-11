# LifeOS release checklist

Before considering a release ready:

- [ ] Confirm the change solves a specific user problem.
- [ ] Review the full diff for accidental edits and secrets.
- [ ] Run `npm ci` and `npm run build` inside `frontend`.
- [ ] Confirm CI is green on the commit being released.
- [ ] Confirm GitHub Pages deployment has completed successfully.
- [ ] Open the deployed site in a fresh browser tab.
- [ ] Smoke-test the changed feature on mobile and desktop.
- [ ] Check local storage behavior after refresh.
- [ ] Update README or docs if user-facing behavior changed.
- [ ] Report limitations honestly, especially around local-only data and sync.

A successful build is necessary, but it is not the same as testing the live site.
