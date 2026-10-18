import { DefaultSession } from "next-auth";

declare module "next-auth" {
  interface Session {
    user: DefaultSession["user"] & {
      id: string;
      role?: "admin" | "user";
      plan?: string;
      provider?: string;
      email_verified?: boolean;
    };
  }

  interface User {
    role?: "admin" | "user";
    plan?: string;
    email_verified?: boolean;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    role?: "admin" | "user";
    plan?: string;
    provider?: string;
    email_verified?: boolean;
  }
}
