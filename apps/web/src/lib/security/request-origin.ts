/**
 * Compare Origin/Referer values against exact trusted origins.
 *
 * Reverse proxies may expose an internal req.nextUrl origin, so callers pass
 * both that origin and canonical/forwarded production origins. No suffix or
 * wildcard matching is used.
 */
export function originMatches(
  candidate: string | null,
  trustedOrigins: Array<string | null | undefined>,
): boolean {
  if (!candidate) return true;

  let candidateOrigin: string;
  try {
    candidateOrigin = new URL(candidate).origin;
  } catch {
    return false;
  }

  return trustedOrigins.some((trusted) => {
    if (!trusted) return false;
    try {
      return new URL(trusted).origin === candidateOrigin;
    } catch {
      return false;
    }
  });
}
