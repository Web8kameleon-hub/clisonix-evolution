# Legacy npm (isolated)

This folder is intentionally managed by **npm only** for old/legacy packages,
while the project root remains on **Yarn Berry**.

## Why

- Keep old package constraints isolated.
- Avoid conflicts with root PnP/Yarn Berry setup.
- Allow `npm i` for legacy dependencies safely.

## Usage (PowerShell)

```powershell
Set-Location "c:\Users\pc\Desktop\ultrawebthinking-RESTORED\legacy-npm"

# Add legacy package(s)
npm install commander
npm install fast-glob zod

# Remove legacy package
npm uninstall commander

# Show installed legacy deps
npm ls --depth=0
```

PowerShell note: do not type `< >` placeholders literally; use real package names as shown above.

## Important

- Run npm commands **only inside** this folder.
- Do not run `npm install` at project root unless explicitly needed.
