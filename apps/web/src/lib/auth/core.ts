import NextAuth from "next-auth";
import Google from "next-auth/providers/google";

const googleClientId =
  process.env.AUTH_GOOGLE_ID || process.env.GOOGLE_CLIENT_ID || "";
const googleClientSecret =
  process.env.AUTH_GOOGLE_SECRET || process.env.GOOGLE_CLIENT_SECRET || "";
const googleHostedDomain = process.env.AUTH_GOOGLE_HD?.trim() || undefined;

const hasGoogleProvider = Boolean(googleClientId && googleClientSecret);

const providers = [];

if (hasGoogleProvider) {
  providers.push(
    Google({
      clientId: googleClientId,
      clientSecret: googleClientSecret,
      allowDangerousEmailAccountLinking: false,
      authorization: {
        params: {
          prompt: "select_account",
          access_type: "offline",
          response_type: "code",
          include_granted_scopes: true,
          ...(googleHostedDomain ? { hd: googleHostedDomain } : {}),
        },
      },
      profile(profile) {
        return {
          id: profile.sub,
          name: profile.name,
          email: profile.email,
          image: profile.picture,
          email_verified: profile.email_verified,
          aud: profile.aud,
        };
      },
    }),
  );
}

const envAuthSecret =
  process.env.AUTH_SECRET?.trim() || process.env.NEXTAUTH_SECRET?.trim() || "";

const authSecret =
  envAuthSecret ||
  (process.env.NODE_ENV !== "production"
    ? "clisonix-dev-auth-secret-change-this"
    : undefined);

if (!authSecret && process.env.NODE_ENV === "production") {
  throw new Error(
    "Missing Auth secret: set AUTH_SECRET or NEXTAUTH_SECRET in production.",
  );
}

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
      if (account?.provider && !user.email) {
        return false;
      }

      if (account?.provider === "google") {
        const googleProfile = profile as
          | { email_verified?: unknown }
          | undefined;
        if (googleProfile?.email_verified !== true) {
          return false;
        }
      }

      return true;
    },
    async session({ session, token }) {
      if (session.user) {
        const userWithId = session.user as {
          id?: string;
          email_verified?: boolean;
          provider?: string;
        };
        userWithId.id =
          (token.sub as string | undefined) ||
          (token.email as string | undefined) ||
          "";
        userWithId.email_verified = (token.email_verified as boolean) ?? true;
        userWithId.provider = token.provider as string | undefined;
      }
      return session;
    },
    async jwt({ token, user, account, profile }) {
      // Store initial user data from provider
      if (user) {
        token.sub = user.id;
        token.email = user.email;
      }

      // Store provider info for retention tracking
      if (account) {
        token.provider = account.provider;
        token.provider_account_id = account.providerAccountId;
        token.expires_at = account.expires_at;
      }

      // Track email verification status from Google profile
      if (
        profile &&
        typeof profile === "object" &&
        "email_verified" in profile
      ) {
        token.email_verified =
          (profile as { email_verified?: unknown }).email_verified === true;
      }

      // Set issued_at for session tracking (365-day retention)
      if (!token.iat) {
        token.iat = Math.floor(Date.now() / 1000);
      }

      return token;
    },
  },
});
