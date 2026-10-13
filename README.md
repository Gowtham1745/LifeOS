# LifeOS

**A calm personal operating system for tasks, habits, goals, and money.**

🌐 **Live:** https://gowtham1745.github.io/LifeOS/

LifeOS is a local-first React + TypeScript dashboard designed to make everyday progress visible without turning productivity into noise.

## What works

- Overview dashboard with momentum score
- Task inbox with add, complete, and delete
- Habit tracker with daily completion and streaks
- Goals with visual progress
- Finance snapshot and recent transactions
- Dark / light mode
- Responsive desktop, tablet, and mobile layouts
- Daily check-in streak
- JSON backup export and restore
- Resettable demo data
- GitHub Pages continuous deployment

## Privacy

The public demo stores its working data in your browser's local storage. Backups are exported as JSON and must be saved somewhere you control; they are not uploaded automatically. The static GitHub Pages site does not require an account or send your dashboard data to a LifeOS cloud service.

**Important:** this repository is public, so never commit passwords, API keys, private credentials, or personal secrets.

## Run locally

```powershell
cd frontend
npm ci
npm run dev
```

For a production build:

```powershell
npm run build
npm run preview
```

The GitHub Actions workflow builds the frontend and publishes `frontend/dist` to GitHub Pages on every push to `main`.

## Tech

React 19 · TypeScript · Vite · Lucide React · GitHub Actions · GitHub Pages

Built by **Gowtham A**.


## First-time setup

1. Open the live site and enter a display name.
2. Add tasks, habits, goals, notes, journal entries, and events from the navigation.
3. Use the theme button to switch between dark and light appearance.
4. Open **Account & Settings** to review the device-only profile and logout options.

## Data and device boundaries

LifeOS currently runs as a static, local-first application. Your entries are stored in the browser on the device you use. They are not automatically synchronized to another phone, browser, or computer. Private browsing sessions and browser profiles may also keep separate storage. Browser storage can be cleared by the browser or device, so use the backup/export feature before resetting or clearing data.

The name field is a display name, not a verified identity. Do not store passwords, financial account credentials, health details, or other sensitive information in LifeOS.

## Contribution workflow

For a small, reviewable change:

1. Make one focused improvement.
2. Run `npm run build` from `frontend`.
3. Review the diff and commit with a descriptive message.
4. Confirm the **LifeOS CI** and **Deploy LifeOS** workflows finish successfully.

Prefer meaningful, tested improvements over empty commits. GitHub contribution intensity is based on qualifying activity and varies with the account's contribution settings.
