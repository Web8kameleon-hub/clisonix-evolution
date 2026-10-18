# Dynamic Ocean Voice and PWA/TWA installation

Date: 2026-10-13  
Branch: `release/dynamic-voice-pwa-twa`

## Scope

- Discover supported Ocean Voice languages and voices dynamically from the runtime instead of maintaining a three-language allow-list.
- Expose voice capabilities through the web API and render language and voice selectors from those capabilities.
- Improve Albanian voice turn handling with a longer silence window and report detected-language confidence.
- Keep voice available through a bounded guest identity when account authentication is unavailable.
- Normalize internal authentication responses across the supported response field variants.
- Provide one global, always-visible install control for the PWA.
- Use the native PWA prompt when available and show platform-specific manual instructions otherwise.
- Expose TWA installation only when a real distribution URL is configured.
- Remove the duplicate install implementation from the Modules page.
- Make the documentation path validator tolerate empty Markdown files instead of throwing on null content.

## Configuration

- `TWA_INSTALL_URL`: real Android distribution or Play Store URL.
- `TWA_PACKAGE_ID`: optional; defaults to `com.clisonix.app`.
- `VOICE_DEFAULT_LANGUAGE`: optional preferred voice language.
- `VOICE_CAPABILITY_TTL_SECONDS`: optional voice-registry cache lifetime.

## Verification

- `python -m py_compile services/ocean-voice-stt/app.py`
- `node --experimental-strip-types apps/web/scripts/verify-ocean-voice-capabilities.ts`

The verification script covers capability normalization, language selection, and invalid capability payload handling.

The documentation validator now completes its scan and reports the repository's existing broken local references instead of terminating on an empty file.
