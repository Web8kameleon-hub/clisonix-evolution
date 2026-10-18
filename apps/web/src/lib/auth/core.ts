import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";

type InternalLoginResponse = {
  success?: boolean;
  valid?: boolean;
  access_token?: string;
  session?: { access_token?: string };
  user?: {
    id?: string;
    user_id?: string;
    email?: string;
    username?: string | null;
    display_name?: string | null;
    role?: string;
    plan?: string;
  };
};

async function verifyInternalCredentials(emailOrUsername: string, password: string) {
  const authBaseUrl = process.env.AUTH_INTERNAL_URL?.trim().replace(/\/+$/, "");
  if (!authBaseUrl) {
    throw new Error("Missing AUTH_INTERNAL_URL.");
  }

  const response = await fetch(`${authBaseUrl}/api/users/login`, {
    method: "POST",
    cache: "no-store",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email_or_username: emailOrUsername,
      password,
    }),
    signal: AbortSignal.timeout(6000),
  });

  if (response.status === 401) {
    return null;
  }
  if (!response.ok) {
    throw new Error(`Internal authentication failed with HTTP ${response.status}.`);
  }

  const result = (await response.json()) as InternalLoginResponse;
  const user = result.user;
  const userId = user?.user_id || user?.id;
  const succeeded = result.success ?? result.valid;
  if (!succeeded || !userId || !user?.email || !result.access_token) {
    throw new Error("Internal authentication returned an invalid response.");
  }

  return {
    id: userId,
    email: user.email,
    name: user.display_name || user.username || user.email,
    role: ["admin", "superadmin"].includes(user.role || "") ? ("admin" as const) : ("user" as const),
    plan: user.plan || "",
    internalAccessToken: result.access_token,
  };
}

const providers = [
  Credentials({
    name: "Clisonix Internal",
    credentials: {
      email: { label: "Email", type: "email" },
      password: { label: "Password", type: "password" },
    },
    async authorize(credentials) {
      const email = String(credentials?.email || "").trim();
      const password = String(credentials?.password || "");
      if (!email || !password) {
        return null;
      }

      const user = await verifyInternalCredentials(email, password);
      if (!user) {
        return null;
      }

      return {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
        plan: user.plan,
        email_verified: true,
        internalAccessToken: user.internalAccessToken,
      };
    },
  }),
];

const envAuthSecret =
  process.env.AUTH_SECRET?.trim() || process.env.NEXTAUTH_SECRET?.trim() || "";

const authSecret = envAuthSecret || undefined;

// Auth.js validates the secret when authentication requests are handled.
// Do not throw during module import: Next.js imports this route at build time.


export const { handlers, auth, signIn, signOut } = NextAuth({
  trustHost: true,
  secret: authSecret,
  providers,
  pages: {
    signIn: "/sign-in",
    error: "/sign-in",
  },
  session: {
    strategy: "jwt",
    maxAge: 60 * 60 * 24 * 365, // 365 days for user registration retention
    updateAge: 60 * 60 * 24, // Update daily
  },
  jwt: {
    maxAge: 60 * 60 * 24 * 365, // 365 days
  },
  callbacks: {
    async signIn({ user, account, profile }) {
      if (!user.email) {
        return false;
      }

      return true;
    },
    async session({ session, token }) {
      if (session.user) {
        const userWithId = session.user as {
          id?: string;
          email_verified?: boolean;
          provider?: string;
          role?: "admin" | "user";
          plan?: string;
        };
        userWithId.id =
          (token.sub as string | undefined) ||
          (token.email as string | undefined) ||
          "";
        userWithId.email_verified = (token.email_verified as boolean) ?? true;
        userWithId.provider = token.provider as string | undefined;
        userWithId.role = token.role as "admin" | "user" | undefined;
        userWithId.plan = token.plan as string | undefined;
      }
      return session;
    },
    async jwt({ token, user, account, profile }) {
      if (user) {
        token.sub = user.id;
        token.email = user.email;
        token.role = (user as { role?: "admin" | "user" }).role;
        token.plan = (user as { plan?: string }).plan;
        token.internalAccessToken = (user as { internalAccessToken?: string }).internalAccessToken;
        token.email_verified =
          (user as { email_verified?: boolean }).email_verified ?? true;
      }

      // Resolve revocation and billing state from the same durable user registry.
      // The backend token stays inside the encrypted Auth.js cookie, never in Session.
      if (!token.internalAccessToken || !process.env.AUTH_INTERNAL_URL) return null;
      const response = await fetch(
        `${process.env.AUTH_INTERNAL_URL.replace(/\/+$/, "")}/api/users/validate-token`, {
          method: "POST", cache: "no-store",
          headers: { Authorization: `Bearer ${token.internalAccessToken}` },
          signal: AbortSignal.timeout(6000),
        },
      );
      if (response.status === 401) return null;
      if (!response.ok) throw new Error("Central authentication is unavailable");
      const state = (await response.json()) as InternalLoginResponse;
      if (!state.valid || state.user?.user_id !== token.sub) return null;
      token.plan = state.user.plan;
      token.role = ["admin", "superadmin"].includes(state.user.role || "") ? "admin" : "user";

      if (account) {
        token.provider = account.provider;
        token.expires_at = account.expires_at;
      }
      if (!token.iat) {
        token.iat = Math.floor(Date.now() / 1000);
      }

      return token;
    },
  },
});
