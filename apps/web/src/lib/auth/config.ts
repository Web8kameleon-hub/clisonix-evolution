export type AuthProvider = "nextauth" | "clisonix";

function normalizeProvider(raw: string | undefined): AuthProvider {
  const value = (raw || "").trim().toLowerCase();
  return value === "nextauth" ? "nextauth" : "clisonix";
}

export function getAuthProvider(): AuthProvider {
  return normalizeProvider(
    process.env.AUTH_PROVIDER || process.env.NEXT_PUBLIC_AUTH_PROVIDER,
  );
}

export function isClisonixAuthProvider(): boolean {
  return getAuthProvider() === "clisonix";
}
