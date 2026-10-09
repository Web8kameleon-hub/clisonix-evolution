/**
 * Clisonix Cloud - Sign Up Page
 *
 * @author Ledjan Ahmati
 * @copyright 2026 Clisonix Cloud
 */

"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { getProviders, useSession } from "next-auth/react";
import { trackEconomy } from "@/lib/economy/track";

async function startOAuth(provider: "google", callbackUrl = "/app") {
  const csrfResponse = await fetch("/api/auth/csrf", { cache: "no-store" });
  if (!csrfResponse.ok) {
    throw new Error("Unable to initialize sign-up.");
  }

  const csrfPayload = (await csrfResponse.json()) as { csrfToken?: string };
  if (!csrfPayload.csrfToken) {
    throw new Error("Missing CSRF token for sign-up.");
  }

  const form = document.createElement("form");
  form.method = "POST";
  form.action = `/api/auth/signin/${provider}`;

  const csrfInput = document.createElement("input");
  csrfInput.type = "hidden";
  csrfInput.name = "csrfToken";
  csrfInput.value = csrfPayload.csrfToken;

  const callbackInput = document.createElement("input");
  callbackInput.type = "hidden";
  callbackInput.name = "callbackUrl";
  callbackInput.value = callbackUrl;

  form.appendChild(csrfInput);
  form.appendChild(callbackInput);
  document.body.appendChild(form);
  form.submit();
}

export default function SignUpPage() {
  const { status } = useSession();
  const searchParams = useSearchParams();
  const [providerState, setProviderState] = useState({ google: false });
  const [providersResolved, setProvidersResolved] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [providerError, setProviderError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;
    const timeoutId = window.setTimeout(() => {
      if (!isActive) return;
      setProviderState({ google: false });
      setProviderError(
        "Sign-up options are unavailable right now. You can browse public modules while access is being restored.",
      );
      setProvidersResolved(true);
    }, 4000);

    getProviders()
      .then((providers) => {
        if (!isActive) return;
        window.clearTimeout(timeoutId);
        setProviderState({
          google: Boolean(providers?.google),
        });
        setProviderError(null);
        setProvidersResolved(true);
      })
      .catch(() => {
        if (!isActive) return;
        window.clearTimeout(timeoutId);
        setProviderState({ google: false });
        setProviderError(
          "Sign-up options could not be loaded. Public modules remain available while access is restored.",
        );
        setProvidersResolved(true);
      });

    return () => {
      isActive = false;
      window.clearTimeout(timeoutId);
    };
  }, []);

  useEffect(() => {
    if (status === "authenticated") {
      window.location.href = "/app";
    }
  }, [status]);

  const authError = searchParams.get("error");
  const authErrorMessage = useMemo(() => {
    if (!authError) return null;
    if (["AccessDenied", "OAuthSignin", "OAuthCallbackError", "CallbackRouteError"].includes(authError)) {
      return "Google sign-up is currently restricted. Switch the OAuth consent screen to External or add the account as a test user.";
    }
    if (authError === "Configuration") {
      return "Authentication is configured incorrectly. Check Google client ID, secret, and redirect URL.";
    }
    return "Sign-up failed. Please try again or contact the administrator.";
  }, [authError]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="relative z-10 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-blue-500 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-xl">C</span>
            </div>
            <span className="text-2xl font-bold text-white">Clisonix Cloud</span>
          </div>
          <p className="text-gray-400">Create your account to get started.</p>
        </div>

        <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-6 text-center">
          <div className="space-y-3">
            {providerState.google ? (
              <button
                type="button"
                onClick={async () => {
                  setSubmitError(null);
                  trackEconomy({
                    economy_code: "CTA",
                    slot: "auth",
                    placement_id: "google-sign-up",
                  });
                  try {
                    await startOAuth("google", "/app");
                  } catch (error) {
                    setSubmitError(error instanceof Error ? error.message : "Google sign-up failed.");
                  }
                }}
                className="w-full rounded-lg bg-white px-4 py-3 font-medium text-black hover:bg-slate-200"
              >
                Continue with Google
              </button>
            ) : null}

            {!providersResolved ? (
              <p className="text-gray-300 text-sm">Loading sign-up options...</p>
            ) : null}

            {providersResolved && !providerState.google ? (
              <div className="space-y-3">
                <p className="text-gray-300 text-sm">
                  {providerError ||
                    "Google sign-up is not configured in this environment yet."}
                </p>
                <div className="grid gap-2">
                  <a
                    href="/modules"
                    className="w-full rounded-lg border border-slate-600 px-4 py-3 text-sm font-medium text-slate-100 hover:bg-slate-700"
                  >
                    Continue in Public Mode
                  </a>
                  <a
                    href="/status"
                    className="w-full rounded-lg border border-slate-700 px-4 py-3 text-sm text-slate-300 hover:bg-slate-700/60"
                  >
                    View Platform Status
                  </a>
                </div>
              </div>
            ) : null}
          </div>

          {authErrorMessage ? (
            <div className="mt-4 rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-left text-sm text-amber-100">
              {authErrorMessage}
            </div>
          ) : null}

          {submitError ? (
            <div className="mt-3 rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-left text-sm text-red-200">
              {submitError}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
