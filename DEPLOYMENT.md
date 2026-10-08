# LifeOS deployment

LifeOS is intentionally split into two parts:

- **Frontend:** React/Vite on GitHub Pages.
- **API:** FastAPI + PostgreSQL on a server.

GitHub Pages is static hosting, so the FastAPI API cannot run inside the Pages site. The frontend is already prepared to use `VITE_API_URL` when the API is deployed.

## Production flow

1. Deploy the `backend/` service using `render.yaml` (or another Docker-compatible host).
2. Give the API a persistent PostgreSQL `DATABASE_URL`.
3. Set `SECRET_KEY` to a long random value.
4. Allow the frontend origin `https://gowtham1745.github.io` in `BACKEND_CORS_ORIGINS`.
5. In the GitHub repository, create a repository **Actions variable** named `LIFEOS_API_URL` containing the HTTPS API URL.
6. Push to `main`. The Pages workflow builds the frontend with that API URL.
7. Users can then create their own LifeOS accounts. Their workspace state is stored against their account and automatically synced between supported devices.

## Local development

Without `VITE_API_URL`, the frontend deliberately remains local-first so the UI can still be developed without a backend. With an API URL configured, the account screen and cloud sync are enabled.

## Important production rule

Never commit `.env`, database credentials, API keys, or production secrets to GitHub.
