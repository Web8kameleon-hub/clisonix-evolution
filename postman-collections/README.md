# Postman Collections

This directory stores Postman collections only for public publishing and sharing.

## Collections

| Collection | Description | Key |
| ---------- | ----------- | --- |
| `Protocol_Kitchen_Sovereign_System.postman_collection.json` | Core protocol tests | `sovereign` |
| `clisonix-ultra-mega-collection.json` | Comprehensive API tests | `ultra-mega` |
| `Clisonix_Cloud_API.postman_collection.json` | Main cloud service tests | `cloud-api` |
| `Clisonix-Cloud-Real-APIs.postman_collection.json` | Production endpoint tests | `real-apis` |
| `clisonix-cloud.postman_collection.json` | Standard test suite | `main` |

## Public Thunder Client / VS Code

We include a public export of the Thunder Client collections and environments for quick use in VS Code.

Files:

- `public/thunderCollection.json` — Thunder Client collection (public)
- `public/thunderEnvironment.json` — Thunder Client environment with production hostnames (replace tokens before running)

Import these into Thunder Client (VS Code) via the Thunder Client import UI.

## Policy

- Postman is publish-only in this repository.
- No runtime sync or internal execution is required for Postman collections.
- For internal operational testing, use Thunder Client and Excel Core flows.

## Updating Public Collections

1. Add or update collection files in this directory.
2. Keep public Thunder files in `public/` updated.
3. Publish the updated files through your standard release/deploy process.
