/**
 * User Profile API
 * GET /api/user/profile - Get current user profile
 * PUT /api/user/profile - Update user profile
 *
 * Production: Connect to PostgreSQL database
 * Development: Returns config-based user data
 */

import { currentUser } from "@/lib/auth/server";
import { apiError, apiSuccess } from "@/lib/api/response";

export async function GET() {
  try {
    const user = await currentUser();
    if (!user) {
      return apiError("UNAUTHORIZED", "Authentication required", {
        status: 401,
      });
    }

    const primaryEmail = user.emailAddresses?.[0]?.emailAddress;
    if (!primaryEmail) {
      return apiError("USER_EMAIL_MISSING", "User email is required", {
        status: 400,
      });
    }

    const profile = {
      id: user.id,
      name:
        [user.firstName, user.lastName].filter(Boolean).join(" ") ||
        user.fullName ||
        "",
      email: primaryEmail,
      avatar: user.imageUrl || null,
      plan: process.env.USER_PLAN || "",
      company: process.env.USER_COMPANY || "",
      phone: process.env.USER_PHONE || "",
      timezone: process.env.USER_TIMEZONE || "",
      language: process.env.USER_LANGUAGE || "",
      createdAt:
        typeof user.createdAt === "number"
          ? new Date(user.createdAt).toISOString()
          : new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    return apiSuccess(profile, {
      meta: {
        source: "next-auth",
      },
    });
  } catch (error) {
    console.error("Profile fetch error:", error);
    return apiError("PROFILE_FETCH_FAILED", "Failed to fetch profile", {
      status: 500,
      details: String(error),
    });
  }
}

export async function PUT(request: Request) {
  try {
    await request.json();

    return apiError(
      "PROFILE_WRITE_NOT_CONFIGURED",
      "Profile write endpoint is not configured for persistent storage",
      {
        status: 501,
      },
    );
  } catch (error) {
    console.error("Profile update error:", error);
    return apiError("PROFILE_UPDATE_FAILED", "Failed to update profile", {
      status: 500,
      details: String(error),
    });
  }
}
