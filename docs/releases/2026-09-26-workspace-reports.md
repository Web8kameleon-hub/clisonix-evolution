# Workspace report routing and source contract

## Issue

The workspace posted `/api/v1/commands/execute` to the generic Ocean ingress,
although the existing owner is Main API. Runtime OpenAPI inspection on September
23 confirmed the command, reader and report routes on Main API and their absence
on Ocean. The form also sent an empty source list, which Main API rejects.

## Documentation

Nginx and Next route only commands, reports and reader to the existing Main API.
Workspace accepts a real URL or UTF-8 text source, forwards its ingestion ID,
preserves backend errors, and sends the API key for polling and downloads.
The entered key stays in component state; existing saved keys remain supported.

Text uploads are limited to 1 GiB (1,073,741,824 bytes), hashed in 1 MiB chunks,
and closed after processing. No copy of the original is written to report storage.
The existing in-process source store retains at most 12,000 bytes of text plus
provenance; this is an excerpt, **not a semantic essence or Film Memory**.
Other document formats remain on the existing Ocean document-ingestion surface.
Report renderers produce source excerpts, not an inference-backed research report.
Job/source stores remain process-local and are not durable across restarts.

Discovery is dynamic and non-cacheable, uses server timestamps, probes registry
entries with known health routes, and leaves unproven states unknown. Ocean uses
its actual `/health` route. Chat sends browser-held conversation context and
keeps transport errors outside assistant messages.

Memory history inspected: `bab3b931` implements browser-local chat history;
`6e7067ea` implements server-side HTTP event queues called stigma film memory;
`29bfedd7` includes keyword tagging and heuristic scoring. These are not proof
of a connected, user-owned semantic essence pipeline. They were not blindly
restored or presented as operational intelligence. That integration is pending.

## Tests

- Eight local API tests passed: real PDF/XLSX/DOCX/PPTX generation and content
  parsing; absent sources; unsupported binary files; exact 1 GiB and 1 GiB + 1.
- Authentication is explicitly overridden only in isolated renderer tests;
  production authentication has not been certified by these tests.
- The size boundary test reads repeated chunks without allocating a 1 GiB
  buffer; this is not an end-to-end 1 GiB network-upload test.
- TypeScript check and existing 19-assertion production-surface check passed.
- Next rewrite contracts passed. The changed Nginx configuration passed
  `nginx -t` in an ephemeral nginx container with temporary test certificates.
- Browser verification could not start because the browser tool rejected its
  environment metadata. Local `/app` requires an authenticated session.
- No production deployment, inference certification or CI-green claim.

## Edge cases

413 for oversized text, 415 for unsupported formats, 422 for empty/unusable text
or missing sources. Uploads close on both success and failure. Failed polling
shows a visible error and retains only the last received job state. Missing keys
are visible; downloads preserve API-key authentication. Raw originals are not
persisted by the reader handler, but multipart parsing may use temporary spooling.

## Benchmark

The eight isolated API tests completed in 2.71 seconds in this Windows environment.
No production latency, throughput or model-quality benchmark was performed.

## Rollback

Revert only the workspace, discovery hook/route, Next rewrites, report reader,
and the three explicit Nginx route prefixes in this patch. Do not reset the
checkout, overwrite user edits, or revert authentication/billing. A rollout still
requires green CI and isolated service validation; neither has occurred here.
