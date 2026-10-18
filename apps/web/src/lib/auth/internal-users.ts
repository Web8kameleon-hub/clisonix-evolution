import { createHash, timingSafeEqual } from "crypto";

export type InternalAuthUser = {
  id: string;
  email: string;
  passwordHash: string;
  name: string;
  role: "admin" | "user";
  plan: string;
};

function hashPassword(password: string): string {
  return createHash("sha256").update(password, "utf8").digest("hex");
}

function normalizeEmail(value: string): string {
  return value.trim().toLowerCase();
}

function parseRole(value: string | undefined): "admin" | "user" {
  return value?.trim().toLowerCase() === "admin" ? "admin" : "user";
}

function parseUserRecord(value: string, index: number): InternalAuthUser | null {
  const parts = value.split("|").map((entry) => entry.trim());
  if (parts.length < 3) {
    return null;
  }

  const [emailRaw, passwordHashRaw, nameRaw, roleRaw, planRaw] = parts;
  const email = normalizeEmail(emailRaw || "");
  const passwordHash = passwordHashRaw || "";
  const name = nameRaw || email;

  if (!email || !passwordHash) {
    return null;
  }

  return {
    id: `internal-${index}-${email}`,
    email,
    passwordHash,
    name,
    role: parseRole(roleRaw),
    plan: planRaw || "mesh_daily",
  };
}

function usersFromList(rawList: string): InternalAuthUser[] {
  return rawList
    .split(";")
    .map((entry, index) => parseUserRecord(entry, index))
    .filter((entry): entry is InternalAuthUser => Boolean(entry));
}

export function getInternalAuthUsers(): InternalAuthUser[] {
  const rawList = process.env.AUTH_INTERNAL_USERS?.trim() || "";
  if (rawList) {
    return usersFromList(rawList);
  }

  const email = normalizeEmail(process.env.AUTH_INTERNAL_EMAIL || "");
  const password = process.env.AUTH_INTERNAL_PASSWORD || "";

  if (!email || !password) {
    return [];
  }

  return [
    {
      id: `internal-0-${email}`,
      email,
      passwordHash: hashPassword(password),
      name: process.env.AUTH_INTERNAL_NAME?.trim() || email,
      role: parseRole(process.env.AUTH_INTERNAL_ROLE),
      plan: process.env.AUTH_INTERNAL_PLAN?.trim() || "mesh_daily",
    },
  ];
}

export function verifyInternalCredentials(emailRaw: string, passwordRaw: string) {
  const email = normalizeEmail(emailRaw);
  const passwordHash = hashPassword(passwordRaw);
  const user = getInternalAuthUsers().find((entry) => entry.email === email);

  if (!user) {
    return null;
  }

  const expected = Buffer.from(user.passwordHash, "hex");
  const actual = Buffer.from(passwordHash, "hex");
  if (expected.length !== actual.length) {
    return null;
  }

  if (!timingSafeEqual(expected, actual)) {
    return null;
  }

  return user;
}
