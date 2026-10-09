"use client";

import { useMemo } from "react";
import {
  signIn as nextAuthSignIn,
  signOut as nextAuthSignOut,
  useSession,
} from "next-auth/react";

type ClientUser = {
  id: string;
  firstName: string | null;
  lastName: string | null;
  fullName: string | null;
  imageUrl: string | null;
  emailAddresses: Array<{ emailAddress: string }>;
  unsafeMetadata: Record<string, unknown>;
  publicMetadata: Record<string, unknown>;
};

function mapUser(data: ReturnType<typeof useSession>["data"]): ClientUser | null {
  const sessionUser = data?.user as
    | {
        id?: string;
        name?: string | null;
        email?: string | null;
        image?: string | null;
      }
    | undefined;

  if (!sessionUser?.email) {
    return null;
  }

  const fullName = sessionUser.name?.trim() || null;
  const [firstName = "", ...rest] = fullName ? fullName.split(" ") : [];
  const lastName = rest.length > 0 ? rest.join(" ") : "";

  return {
    id: sessionUser.id || sessionUser.email,
    firstName: firstName || null,
    lastName: lastName || null,
    fullName,
    imageUrl: sessionUser.image || null,
    emailAddresses: [{ emailAddress: sessionUser.email }],
    unsafeMetadata: {},
    publicMetadata: {},
  };
}

export function useAuth() {
  const { data, status } = useSession();
  const user = mapUser(data);

  return {
    userId: user?.id || null,
    isSignedIn: status === "authenticated" && Boolean(user),
  };
}

export function useUser() {
  const { data, status } = useSession();

  return useMemo(
    () => ({
      user: mapUser(data),
      isLoaded: status !== "loading",
    }),
    [data, status],
  );
}

export async function signIn(provider: string = "google") {
  return nextAuthSignIn(provider);
}

export async function signOut(options?: { callbackUrl?: string }) {
  return nextAuthSignOut(options);
}

export function UserButton({ afterSignOutUrl = "/" }: { afterSignOutUrl?: string }) {
  const { user } = useUser();

  if (!user) {
    return null;
  }

  return (
    <button
      type="button"
      onClick={() => nextAuthSignOut({ callbackUrl: afterSignOutUrl })}
      className="rounded-lg border border-slate-600 px-3 py-1.5 text-sm text-slate-200 hover:bg-slate-700"
    >
      Sign out
    </button>
  );
}
