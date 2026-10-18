"use client";

import { FormEvent, useState } from "react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setMessage(null);
    setError(null);

    try {
      const response = await fetch("/api/auth/password/forgot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim() }),
      });

      const data = await response.json().catch(() => ({}));

      if (response.status === 503) {
        setError(
          "Password recovery email delivery is not configured in this deployment. Contact support for account recovery.",
        );
        return;
      }

      if (!response.ok) {
        setError(data.detail || data.error || "Something went wrong. Please try again.");
        return;
      }

      setMessage(data.message || "If this email exists, a recovery link has been sent.");
    } catch {
      setError("Internal authentication is temporarily unavailable.");
    } finally {
      setSubmitting(false);
    }
  }

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
          <p className="text-gray-400">Recover access to your account.</p>
        </div>

        <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-6">
          {!message ? (
            <form className="space-y-4" onSubmit={submit}>
              <div>
                <label
                  htmlFor="email"
                  className="mb-1 block text-sm font-medium text-slate-200"
                >
                  Account email
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  className="w-full rounded-lg border border-slate-600 bg-slate-900/70 px-3 py-3 text-white outline-none focus:border-purple-400"
                />
              </div>

              <button
                type="submit"
                disabled={submitting || !email.trim()}
                className="w-full rounded-lg bg-gradient-to-r from-purple-500 to-blue-500 px-4 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
              >
                {submitting ? "Sending..." : "Send recovery link"}
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
