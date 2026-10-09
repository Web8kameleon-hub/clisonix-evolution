"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface OpenMindStatus {
  service: string;
  ready: boolean;
  default_model: string;
  ollama_reachable: boolean;
}

export default function OpenMindPage() {
  const [message, setMessage] = useState("");
  const [responseText, setResponseText] = useState("");
  const [provider, setProvider] = useState("ollama");
  const [model, setModel] = useState("");
  const [models, setModels] = useState<string[]>([]);
  const [status, setStatus] = useState<OpenMindStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [statusRes, modelsRes] = await Promise.all([
          fetch("/api/openmind?path=status", { cache: "no-store" }),
          fetch("/api/openmind?path=models", { cache: "no-store" }),
        ]);

        const readJsonSafe = async (res: Response) => {
          const text = await res.text();
          try {
            return text ? JSON.parse(text) : {};
          } catch {
            return {
              status: "error",
              message: "Invalid JSON response from OpenMind proxy",
              raw: text.slice(0, 500),
            };
          }
        };

        const statusData = await readJsonSafe(statusRes);
        const modelsData = await readJsonSafe(modelsRes);

        setStatus(statusData);
        const list = Array.isArray(modelsData?.models) ? modelsData.models : [];
        setModels(list);
        setModel(statusData?.default_model || list[0] || "llama3.1:8b");
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Failed to load OpenMind");
      }
    };

    load();
  }, []);

  const sendMessage = async () => {
    if (!message.trim() || loading) return;
    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/openmind", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          provider,
          model,
          options: {},
        }),
      });

      const raw = await res.text();
      let data: any = {};
      try {
        data = raw ? JSON.parse(raw) : {};
      } catch {
        data = { message: raw || "Invalid OpenMind response" };
      }
      if (!res.ok) {
        setError(data?.detail || data?.message || "OpenMind request failed");
        return;
      }

      setResponseText(typeof data?.response === "string" ? data.response : JSON.stringify(data, null, 2));
    } catch (sendError) {
      setError(sendError instanceof Error ? sendError.message : "OpenMind request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white text-slate-900 px-4 py-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">OpenMind</h1>
          <Link href="/modules" className="text-sm text-slate-600 hover:text-slate-900">
            ← Modules
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="border border-slate-200 rounded-lg p-3">
            <p className="text-xs text-slate-500">Service</p>
            <p className="text-sm font-medium">{status?.service || "openmind"}</p>
          </div>
          <div className="border border-slate-200 rounded-lg p-3">
            <p className="text-xs text-slate-500">Ready</p>
            <p className="text-sm font-medium">{status?.ready ? "Yes" : "No"}</p>
          </div>
          <div className="border border-slate-200 rounded-lg p-3">
            <p className="text-xs text-slate-500">Ollama</p>
            <p className="text-sm font-medium">{status?.ollama_reachable ? "Reachable" : "Unavailable"}</p>
          </div>
        </div>

        <div className="border border-slate-200 rounded-lg p-4 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <label className="text-sm space-y-1 block">
              <span className="text-slate-600">Provider</span>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                className="w-full border border-slate-300 rounded-md px-3 py-2"
              >
                <option value="ollama">ollama</option>
                <option value="openmind">openmind</option>
              </select>
            </label>

            <label className="text-sm space-y-1 block">
              <span className="text-slate-600">Model</span>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full border border-slate-300 rounded-md px-3 py-2"
              >
                {models.length === 0 && <option value={model || "llama3.1:8b"}>{model || "llama3.1:8b"}</option>}
                {models.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={5}
            placeholder="Write a prompt for OpenMind..."
            className="w-full border border-slate-300 rounded-md px-3 py-2"
          />

          <button
            onClick={sendMessage}
            disabled={loading || !message.trim()}
            className="px-4 py-2 rounded-md bg-slate-900 text-white disabled:opacity-50"
          >
            {loading ? "Sending..." : "Send"}
          </button>

          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>

        <div className="border border-slate-200 rounded-lg p-4">
          <p className="text-sm font-medium mb-2">Response</p>
          <pre className="text-sm whitespace-pre-wrap break-words text-slate-800">{responseText || "No response yet."}</pre>
        </div>
      </div>
    </div>
  );
}
