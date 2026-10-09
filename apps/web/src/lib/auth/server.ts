import { auth as getSession } from "@/lib/auth/core";

type AuthSession = {
  user?: {
    id?: string;
    email?: string | null;
    name?: string | null;
    image?: string | null;
  } | null;
} | null;

type SessionUser = {
  id: string;
  email: string;
  name?: string | null;
  image?: string | null;
};

type AppUser = {
  id: string;
  firstName: string | null;
  lastName: string | null;
  fullName: string | null;
  imageUrl: string | null;
  createdAt: number;
  emailAddresses: Array<{ emailAddress: string }>;
  unsafeMetadata: Record<string, unknown>;
  publicMetadata: Record<string, unknown>;
};

function toSessionUser(session: AuthSession): SessionUser | null {
  const user = session?.user || undefined;

  if (!user?.email) {
    return null;
  }

  return {
    id: user.id || user.email,
    email: user.email,
    name: user.name,
    image: user.image,
  };
}

function toAppUser(user: SessionUser | null): AppUser | null {
  if (!user) {
    return null;
  }

  const fullName = user.name?.trim() || null;
  const [firstName = "", ...rest] = fullName ? fullName.split(" ") : [];
  const lastName = rest.length > 0 ? rest.join(" ") : "";

  return {
    id: user.id,
    firstName: firstName || null,
    lastName: lastName || null,
    fullName,
    imageUrl: user.image || null,
    createdAt: Date.now(),
    emailAddresses: [{ emailAddress: user.email }],
    unsafeMetadata: {},
    publicMetadata: {},
  };
}

export async function auth() {
  const session = await getSession();
  const user = toSessionUser(session);

  return {
    userId: user?.id || null,
    sessionClaims: session,
  };
}

export async function currentUser() {
  const session = await getSession();
  return toAppUser(toSessionUser(session));
}
