# Privacy and data handling

## Current storage model

The GitHub Pages version is a static, local-first web application. Profile details and entries are stored in browser local storage on the current browser and device.

## What this means

- A profile on one device does not automatically appear on another device.
- Clearing browser site data may erase saved entries.
- Private/incognito sessions may discard data when closed.
- A display name is not identity verification or authentication.
- The current public static deployment should not be described as providing secure cloud accounts or cross-device synchronization.

## Safer use

Do not enter passwords, bank credentials, government identifiers, or sensitive personal details. Export a backup before clearing browser storage or resetting the application.

## Future sync

Any future cross-device feature must use a real hosted backend, authenticated sessions, per-user access controls, secure transport, backup/retention rules, and tests proving users cannot read each other's data. Do not store account passwords in local storage.
