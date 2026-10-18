"use client";

import { FormEvent, Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") || "";
  const [newPassword, setNewPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setMessage(null);
    setError(null);

    try {
      const response = await fetch("/api/auth/password/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: newPassword }),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        setError(data.detail || data.error || "This recovery link is invalid or has expired.");
        return;
      }

      setMessage(data.message || "Password updated. You can sign in with your new password now.");
    } catch {
      setError("Internal authentication is temporarily unavailable.");
    } finally {
      setSubmitting(false);
    }
  }

  if (!token) {
    return (
      <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-3 text-sm text-red-100">
        This recovery link is missing its token. Request a new one from the{" "}
        <a href="/forgot-password" className="underline">
          forgot password
        </a>{" "}
        page.
      </div>
    );
  }

  return (
    <>
      {!message ? (
        <form className="space-y-4" onSubmit={submit}>
          <div>
            <label
              htmlFor="new_password"
              className="mb-1 block text-sm font-medium text-slate-200"
            >
              New password
            </label>
            <input
              id="new_password"
              name="new_password"
              type="password"
              autoComplete="new-password"
              required
              minLength={8}
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
              className="w-full rounded-lg border border-slate-600 bg-slate-900/70 px-3 py-3 text-white outline-none focus:border-purple-400"
            />
          </div>

          <button
            type="submit"
            disabled={submitting || newPassword.length < 8}
            className="w-full rounded-lg bg-gradient-to-r from-purple-500 to-blue-500 px-4 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
          >
            {submitting ? "Updating..." : "Set new password"}
          </button>
        </form>
      ) : (
        <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3 py-3 text-sm text-emerald-100">
          {message}
        </div>
      )}

      {error ? (
        <div
          role="alert"
          className="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-200"
        >
          {error}
        </div>
      ) : null}
    </>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="relative z-10 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-xl">C</span>
            </div>
            <span className="text-2xl font-bold text-white">Clisonix Cloud</span>
          </div>
          <p className="text-gray-400">Set a new password for your account.</p>
        </div>

        <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-6">
          <Suspense fallback={<p className="text-center text-sm text-gray-300">Loading...</p>}>
            <ResetPasswordForm />
          </Suspense>

          <div className="mt-5 border-t border-slate-700 pt-4 text-center">
            <a
              href="/sign-in"
              className="text-sm text-purple-300 hover:text-purple-200"
            >
              Back to sign in
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
