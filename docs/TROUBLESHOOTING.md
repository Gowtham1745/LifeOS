# Troubleshooting LifeOS

## The page is blank

- Refresh the page once.
- Open the browser developer console and inspect the first error.
- Confirm the latest GitHub Pages deployment succeeded.
- If a new change caused the issue, inspect the latest commit before making another change.

## My entries disappeared

LifeOS stores entries in local browser storage. Check that you are using the same browser profile and device. Private browsing, cleared site data, browser cleanup tools, or a different browser can make local entries unavailable.

## My data does not appear on another device

Cross-device synchronization is not currently enabled in the static GitHub Pages version. A shared URL does not make browser storage shared.

## A change is not visible yet

Check the repository's Actions tab. Wait for the deployment workflow to finish successfully, then reload the site. A hard refresh may be needed if the browser cached old assets.

## Report a reproducible issue

Include the page name, steps to reproduce, expected behavior, actual behavior, browser/device, and screenshot if useful. Never include passwords or private data.
