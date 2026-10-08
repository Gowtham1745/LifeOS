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

The public demo stores its working data in your browser's local storage. The static GitHub Pages site does not require an account or send your dashboard data to a LifeOS cloud service.

**Important:** this repository is public, so never commit passwords, API keys, private credentials, or personal secrets.

## Run locally

```powershell
cd frontend
npm install
npm run dev
```

For a production build:

```powershell
npm run build
```

The GitHub Actions workflow builds the frontend and publishes `frontend/dist` to GitHub Pages on every push to `main`.

## Tech

React 19 · TypeScript · Vite · Lucide React · GitHub Actions · GitHub Pages

Built by **Gowtham A**.
