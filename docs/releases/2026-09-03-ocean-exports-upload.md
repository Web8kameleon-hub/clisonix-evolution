# Ocean Exports And Document Upload

## Issue

Curiosity Ocean PDF and DOCX exports failed, while document uploads did not consistently honor the product contract of 1 GiB by default and `-1` for unlimited uploads.

## Documentation

PDF and DOCX are now generated locally from the existing transcript. Document uploads are streamed as multipart data through the web proxy. `DOCUMENT_MAX_BYTES` defaults to `1073741824`; exactly `-1` disables the application limit. Other non-positive values fall back to 1 GiB. Nginx delegates size enforcement to the application.

Automated production releases use a clean detached worktree of `origin/main`. This preserves any local operational edits in the server's primary checkout and prevents them from contaminating or blocking a release.

## Tests

- `npm run type-check --workspace apps/web`
- `npm run test:ocean-export --workspace apps/web`
- `python -m pytest ocean-core/tests/test_upload_limits.py`
- `AUTH_SECRET=<local-test-secret> npm run build --workspace apps/web`

The broader live Ocean multilingual suite currently receives HTTP 404 from the pre-existing service on port 8030 for `/chat` and reaction routes. This environmental baseline is not counted as a passing release gate.

## Edge cases

- Empty message content is skipped without producing malformed artifacts.
- Multiline text, PDF metacharacters, Albanian Latin characters, and unsupported PDF glyphs are handled deterministically.
- `-1`, zero, invalid negative values, custom positive limits, and the 1 GiB boundary have explicit policy tests.
- Image and audio attachments retain their existing 25 MiB browser limit; the 1 GiB policy applies to documents.
- A dirty server checkout cannot overwrite release code or be overwritten by deployment.

## Benchmark

The benchmark generates both formats from 1,000 messages and requires completion below 5 seconds. Run `npm run benchmark:ocean-export --workspace apps/web`; the measured value is recorded in CI output.

## Rollback

Revert this release commit and redeploy `main`. Restore the previous proxy route and set `DOCUMENT_MAX_BYTES` explicitly if an emergency lower limit is required.
