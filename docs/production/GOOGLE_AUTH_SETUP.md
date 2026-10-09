# Social Auth Setup for Clisonix

## Problem: `Fehler 403: org_internal`

This error means the current Google OAuth app is configured as **Internal** in Google Cloud and only users inside that Google Workspace organization can sign in.

This is **not caused by NextAuth itself**. The Google OAuth project must allow external users.

---

## Required Google Cloud Console Fix

Open:

- `Google Cloud Console`
- `APIs & Services` → `OAuth consent screen`

Then:

1. Set **User type** to **External**
2. If the app is still in testing, add allowed **Test users**
3. Publish the app when ready
4. Ensure these redirect URIs exist:
   - `https://clisonix.com/api/auth/callback/google`
   - `http://localhost:3000/api/auth/callback/google`
   - `http://localhost:3010/api/auth/callback/google`

---

## Environment Variables

### Google

```env
AUTH_GOOGLE_ID=your_google_client_id
AUTH_GOOGLE_SECRET=your_google_client_secret
```

or

```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### Apple

```env
AUTH_APPLE_ID=your_apple_service_id
AUTH_APPLE_SECRET=your_apple_private_key_jwt
```

or

```env
APPLE_CLIENT_ID=your_apple_service_id
APPLE_CLIENT_SECRET=your_apple_private_key_jwt
```

### Shared auth

```env
AUTH_SECRET=replace-with-a-long-random-secret
NEXTAUTH_URL=https://clisonix.com
AUTH_URL=https://clisonix.com
```

---

## Current App Behavior

The app now:

- supports both `Google` and `Apple` providers
- supports both `AUTH_GOOGLE_*` / `GOOGLE_CLIENT_*`
- supports both `AUTH_APPLE_*` / `APPLE_CLIENT_*`
- routes auth errors back to `/sign-in`
- shows a clearer UI message when the provider is restricted or misconfigured

---

## Summary

To allow `clisonix@pm.me` or any other public Gmail account, the Google OAuth app must be switched from **Internal** to **External**.

